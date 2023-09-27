from processlogger import ProcessLogger
import time
import multiprocessing
from multiprocessing import shared_memory
import queue    # imported for using queue.Empty exception
from processravfwriter import ProcessRavfWriter
from otestamper import OteStamper
import threading



# Singleton

class FrameWriter:

	__instance		= None
	SHM_DESTROY_RETRIES	= 20


	def __init__(self):
		if FrameWriter.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			FrameWriter.__instance = self

			self.logger = ProcessLogger.getInstance().getLogger()
			
			self.otestamper			= OteStamper.getInstance()

			self.sharedMemoryCreated	= False
			self.sharedMemoryBuffers	= []
			self.sharedMemoryLocks		= []
			self.sharedMemoryIndex		= 0

			# Setup ProcessRavfWrite as a seperate process
			self.queue_cmd			= multiprocessing.Queue()               # This is outgoing cmd queue
			self.queue_finished		= multiprocessing.Queue()               # This is incoming queue used to signal a frame has been written

			self.processRavfWriter		= ProcessRavfWriter()
			self.process			= multiprocessing.Process(target=self.processRavfWriter.main, args=(ProcessLogger.getInstance().queue, self.queue_cmd, self.queue_finished))
			self.process.start()


	@staticmethod
	def getInstance():
		if FrameWriter.__instance == None:
			if (threading.current_thread() is threading.main_thread()) and multiprocessing.current_process().name == 'main':
				FrameWriter()
			else:
				raise ValueError('ravfwriter: not called from main thread/process')

		return FrameWriter.__instance


	def checkMainThreadProcess(self):
		if not ((threading.current_thread() is threading.main_thread()) and multiprocessing.current_process().name == 'main'):
			raise ValueError('ravfwriter: not called from main thread/process')


	def terminate(self):
		"""
                        Call once from the top process to stop the logging process and terminate the logging process
                """
		self.checkMainThreadProcess()
		self.queue_cmd.put({ 'cmd': 'terminate' })
		self.process.join()
		if self.sharedMemoryCreated:
			self.__SHMDestroy()
			self.sharedMemoryCreated = False


	def startRecordingVideo(self, filename, required_metadata, user_metadata):
		self.checkMainThreadProcess()
		self.queue_cmd.put({ 'cmd': 'startRecording', 'filename': filename, 'required_metadata': required_metadata, 'user_metadata': user_metadata })


	def stopRecordingVideo(self):
		self.checkMainThreadProcess()
		self.queue_cmd.put({ 'cmd': 'stopRecording' })


	def createSharedMemory(self, size):
		self.checkMainThreadProcess()
		if not self.sharedMemoryCreated:
			self.__SHMCreateSHM(size)
			self.queue_cmd.put({ 'cmd': 'createsharedmemory', 'size': size })
			self.sharedMemoryCreated = True


	def writeFrame(self, metadata, frameIndex):
		self.__SHMSendFrame(metadata, frameIndex)


	# Reference: https://stackoverflow.com/questions/73267885/multiprocessing-with-queue-queue-in-python-for-numpy-arrays 
	def __SHMCreateSHM(self, size):
		# Create shared memory
		self.sharedMemoryIndex = 0
		for i in range(ProcessRavfWriter.SHM_FRAME_BUFFERS):
			try:
				shm_buf = shared_memory.SharedMemory(create=True, size=size, name='astrid_frame_%d' % (i))
			except FileExistsError:
				shm_buf = shared_memory.SharedMemory(size=size, name='astrid_frame_%d' % (i))
				shm_buf.close()
				shm_buf.unlink()
				shm_buf = shared_memory.SharedMemory(create=True, size=size, name='astrid_frame_%d' % (i))
			
			self.sharedMemoryBuffers.append(shm_buf)
			self.sharedMemoryLocks.append(False)


	def __SHMProcessWriterCompletes(self):
		# Unlocks the shared memory buffer for reuse when the write is done with it
		while True:
			try:
				ind = self.queue_finished.get_nowait()
			except queue.Empty:
				return
			else:
				self.sharedMemoryLocks[ind] = False


	def __SHMDestroy(self):
		# Destroy shared memory buffers
		for i in range(ProcessRavfWriter.SHM_FRAME_BUFFERS):
			count = 0

			# If the frame is locked, we should wait for the lock to be released
			while self.sharedMemoryLocks[i]:
				if count >= FrameWriter.SHM_DESTROY_RETRIES:
					self.logger.warning('final frame: %d not confirmed written' % i)
					self.otestamper.statistics['finalFrameNotWritten'] += 1
					break
				else:
					self.__SHMProcessWriterCompletes()
					time.sleep(0.1)
				count += 1

			self.sharedMemoryLocks[i] = False
			self.sharedMemoryBuffers[i].close()
			self.sharedMemoryBuffers[i].unlink()


	def __SHMSendFrame(self, frame, metadata):
		# Send a frame via shared memory
		t1 =  time.process_time_ns()

		self.__SHMProcessWriterCompletes()

		count = 0
		while self.sharedMemoryLocks[self.sharedMemoryIndex]:
			if count >= ProcessRavfWriter.SHM_FRAME_BUFFERS:
				self.logger.error('no shared memory buffers available, dropping frame')
				return

			self.sharedMemoryIndex += 1
			self.sharedMemoryIndex %= ProcessRavfWriter.SHM_FRAME_BUFFERS

			count += 1

		self.sharedMemoryBuffers[self.sharedMemoryIndex].buf[:len(frame)] = frame	
		self.sharedMemoryLocks[self.sharedMemoryIndex] = True
		self.logger.debug('queue put')

		self.checkMainThreadProcess()
		self.queue_cmd.put({ 'cmd': 'writeframe', 'metadata': metadata, 'frameIndex': self.sharedMemoryIndex })

		locksUsed = 0
		for lock in self.sharedMemoryLocks:
			if lock:
				locksUsed += 1
		self.logger.debug('shm locks used: %d' % locksUsed)
	
		# Increment sharedMemoryIndex and wrap around
		self.sharedMemoryIndex += 1
		self.sharedMemoryIndex %= ProcessRavfWriter.SHM_FRAME_BUFFERS

		t2 =  time.process_time_ns()
		self.logger.debug('shm write took: %0.6fs' % ((t2-t1)/1000000000.0))
		self.logger.debug('metadata: %s', metadata)
