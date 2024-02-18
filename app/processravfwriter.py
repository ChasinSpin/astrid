from processlogger import ProcessLogger
import logging
import sys
import time
import signal
import queue    # imported for using queue.Empty exception
from multiprocessing import shared_memory
#from ravf import RavfReader, RavfWriter, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox
from ravf import RavfWriter
from datetime import datetime, timedelta



class ProcessRavfWriter:

	SHM_FRAME_BUFFERS = 160

	def __init__(self):
		self.connected = False
		self.recording = False
		self.garbageCollected = False


	def __stopRecording(self):
		if self.recording:
			self.ravf_writer.finish(self.fp)
			self.fp.flush()
			self.fp.close()
			self.fp = None
			self.recording = False
			self.logger.propagate = True


	def __cleanup_handler(self, sig, frame):
		"""
			Called to cleanup when the process exits
		"""
		self.__stopRecording()

		self.__queue_clear(self.queue_finished)
		self.__queue_clear(self.queue_cmd)

		if self.sharedMemoryBuffers is not None:
			for i in range(ProcessRavfWriter.SHM_FRAME_BUFFERS):
				self.sharedMemoryBuffers[i].close()

		self.logger.info('FrameWriterProcess terminated!')
		sys.exit(0)


	def __queue_clear(self, q):
		try:
			while True:
				q.get_nowait()
		except queue.Empty:
			pass


	def main(self, queue_logger, queue_cmd, queue_finished):
		"""
                	main execution loop for this process, writes frames to Ravf format
		"""

		self.logger = ProcessLogger.startChildLogging(queue_logger, name = 'framewriter', logging_level=logging.DEBUG)
		self.logger.info('framewriter process started...')
		self.logger.debug('framewriter queuecmd_size waiting commands: %d' % queue_cmd.qsize())

		# Store the queues we need to read/write to
		self.queue_cmd		= queue_cmd
		self.queue_finished	= queue_finished

		# Setup signal handler so that process signals (e.g. CTRL-C) can kill the process
		signal.signal(signal.SIGINT, self.__cleanup_handler)
		signal.signal(signal.SIGTERM, self.__cleanup_handler)

		self.fp = None

		# Open the shared memory buffers
		self.sharedMemoryBuffers = None

		# Loop waiting and processing commands
		while True:
			queueItem = None
			timedOut = False

			try:
				queueItem = self.queue_cmd.get(timeout=1)
			except queue.Empty:
				if self.recording:
					self.logger.warning('queue get timed out after 1 second')
				timedOut = True
				pass

			if queueItem is None:
				if not timedOut:
					self.logger.warning('queueItem is None')
				continue

			t3 =  time.process_time_ns()

			self.logger.debug('framewriter queue item recv: %s @ %s' % (queueItem, datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')))


			cmd = queueItem['cmd']

			if   cmd == 'writeframe':
				t1 =  time.process_time_ns()

				metadata = queueItem['metadata']
				sharedMemoryBufferIndex = queueItem['frameIndex']

				self.ravf_writer.write_frame( self.fp,
							frame_type              = metadata['frame_type'],
							data = self.sharedMemoryBuffers[sharedMemoryBufferIndex].buf,
							start_timestamp         = metadata['start_timestamp'],
							exposure_duration       = metadata['exposure_duration'],
							satellites              = metadata['satellites'],
							almanac_status          = metadata['almanac_status'],
							almanac_offset          = metadata['almanac_offset'],
							satellite_fix_status    = metadata['satellite_fix_status'],
							sequence                = metadata['sequence'])
				self.fp.flush()
				self.queue_finished.put(sharedMemoryBufferIndex)

				t2 =  time.process_time_ns()
				self.logger.debug('writeFrame took: %0.6fs, completed @ %s, delta completed:%0.6fs' % (((t2-t1)/1000000000.0), datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f'), ((t2-t3)/1000000000.0)))
	
				if self.garbageCollected:
					self.logger.debug('garbage collected on previous frame')
					self.garbageCollected = False

			elif cmd == 'startRecording':
				self.fp			= open(queueItem['filename'], 'wb')	
				self.ravf_writer 	= RavfWriter(file_handle = self.fp, required_metadata_entries = queueItem['required_metadata'], user_metadata_entries = queueItem['user_metadata'])
				self.recording		= True
				self.logger.propagate = False

			elif cmd == 'stopRecording':
				self.__stopRecording()

			elif cmd == 'createsharedmemory':
				if self.sharedMemoryBuffers is None:
					size = queueItem['size']
					self.sharedMemoryBuffers = []
					for i in range(ProcessRavfWriter.SHM_FRAME_BUFFERS):
						shm_buf = shared_memory.SharedMemory(size=size, name='astrid_frame_%d' % (i))
						self.sharedMemoryBuffers.append(shm_buf)

			elif cmd == 'terminate':
				self.logger.info('terminating ProcessRavfWriter')
				break

			else:
				raise ValueError('Unrecognized command: %s' % (cmd))


		# Exit and cleanup
		self.__cleanup_handler(None, None)
