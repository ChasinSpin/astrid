""" RAVF encoder functionality """

from processlogger import ProcessLogger
from ravf import RavfImageFormat, RavfColorType, RavfImageEndianess, RavfMetadataType, RavfFrameType
from picamera2.encoders.encoder import Encoder
from datetime import datetime,timezone
#from request import _MappedBuffer
from picamera2.request import _MappedBuffer
from otestamper import OteStamper
from settings import Settings
from datetime import datetime
import time
import sys
import signal
import queue    # imported for using queue.Empty exception
import multiprocessing
from framewriter import FrameWriter
from processravfwriter import ProcessRavfWriter
from fillinnareport import FillInNAReport

class RavfEncoder(Encoder):

	MINIMUM_FRAME_DURATION_MICROS = 16563	# Maximum frame rate the camera can be set to, for the IMX296 this is just over 60fps

	def __init__(self, filename: str, metadata: dict, camera: object):
		super().__init__()

		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()

		self.camera			= camera
		self.filename			= filename
		self.metadata			= metadata
		
		self.frameHalfDurationMicros	= int(self.metadata['frameDurationMicros']/2.0)
		self.lastTimestamp		= 0
		self.otestamper			= OteStamper.getInstance()
		self.lastSequence		= 0
		self.firstFrame			= True
		self.lastTimeFrame		= 0
		self.lastCameraTimestamp	= 0
		self.syncState			= 0
		self.recording			= False



	def start(self):
		self.recording			= True
		self.firstFrame = True
		self.otestamper.resetStatistics()
		self.otestamper.stopUpdateStatusTimer()
		self.otestamper.startRecordingVideo()
		self.syncState = 0
		self.waiting_frame_count = 14
		super().start()

		# Calculate nanoseconds since 2010 from the system for recording start time
		# Note this time is not necessarily accurate, it's just a guideline
		recording_start_utc = datetime.utcnow()
		self.start_observing_time = (recording_start_utc.hour, recording_start_utc.minute, float(recording_start_utc.second) + (recording_start_utc.microsecond/1000000.0))
		recording_start_utc = time.mktime(recording_start_utc.timetuple())    # Convert to unix epoch
		recording_start_utc -= 1262304000
		recording_start_utc *= 1000000000                                     # Convert to nanoseconds
		recording_start_utc = int(recording_start_utc)

		self.__required_metadata_entries = [
			('COLOR-TYPE',                  int(self.metadata['color_type'].value)),
			('IMAGE-ENDIANESS',             int(RavfImageEndianess.LITTLE_ENDIAN.value)),
			('IMAGE-WIDTH',                 int(self.width)),
			('IMAGE-HEIGHT',                int(self.height)),
			('IMAGE-ROW-STRIDE',            int(self.stride)),
			('IMAGE-FORMAT',                int(self.metadata['image_format'].value)),
			('IMAGE-BINNING-X',             self.metadata['binning'][0]),
			('IMAGE-BINNING-Y',             self.metadata['binning'][1]),
			('FRAME-TIMING-ACCURACY',       int(4)),
			('LATITUDE',                    self.otestamper.status['latitude']), 
			('LONGITUDE',                   self.otestamper.status['longitude']),
			('ALTITUDE',                    self.otestamper.status['altitude']),
			('OBSERVER',                    Settings.getInstance().observer['observer_name']),
			('OBSERVER-ID',                 Settings.getInstance().observer['observer_id']),
			('INSTRUMENT',                  'Astrid'),
			('INSTRUMENT-VENDOR',           'ChasinSpin'),
			('INSTRUMENT-VERSION',          Settings.getInstance().hidden['version']),
			('INSTRUMENT-SERIAL',           '00001'),
			('INSTRUMENT-FIRMWARE-VERSION', '0.9a'),
			('INSTRUMENT-GAIN',             Settings.getInstance().camera['gain']),
			('INSTRUMENT-SENSOR',           self.metadata['sensor']),
			('INSTRUMENT-GAMMA',            1.0),
			('INSTRUMENT-SHUTTER',          self.metadata['shutter_ns']),
			('INSTRUMENT-OFFSET',           0),
			('RECORDER-SOFTWARE',           'Astrid'),
			('RECORDER-SOFTWARE-VERSION',   '0.9a'),
			('RECORDER-HARDWARE',           'OTEStamper'),
			('RECORDER-HARDWARE-VERSION',   '0.9a'),
			('OBJNAME',                     self.metadata['objName']),
			('RA',                          self.metadata['ra']),
			('DEC',                         self.metadata['dec']),
			('EQUINOX',                     0),
			('COMMENT',                     'Astrid RAVF Format'), 
			('RECORDING-START-UTC',         recording_start_utc),
			('TELESCOPE',			self.metadata['telescope']),
		]

		self.logger.info(self.__required_metadata_entries)

		self.__user_metadata_entries = [
			('INSTRUMENT-SENSOR-PIXEL-SIZE-X',	RavfMetadataType.FLOAT32,	self.metadata['sensorPixelSizeX']),
			('INSTRUMENT-SENSOR-PIXEL-SIZE-Y',	RavfMetadataType.FLOAT32,	self.metadata['sensorPixelSizeY']),
			('FOCAL-LENGTH',			RavfMetadataType.FLOAT32,	self.metadata['focalLength']),
			('STATION-NUMBER',			RavfMetadataType.UINT16,	self.metadata['stationNumber']),
			('STATION-HOSTNAME',			RavfMetadataType.UTF8STRING,	self.metadata['hostname']),
			('INSTRUMENT-FRAMES-PER-SECOND',	RavfMetadataType.FLOAT32,	1.0/(self.metadata['shutter_ns']/1000000000.0)),
		]

		if 'occultationPredictedCenterTime' in self.metadata.keys():
			self.__user_metadata_entries.append( ('OCCULTATION-PREDICTED-CENTER-TIME',	RavfMetadataType.UTF8STRING,	self.metadata['occultationPredictedCenterTime']) )

		if 'occultationObjectNumber' in self.metadata.keys():
			self.__user_metadata_entries.append( ('OCCULTATION-OBJECT-NUMBER',		RavfMetadataType.UTF8STRING,	self.metadata['occultationObjectNumber']) )

		if 'occultationObjectName' in self.metadata.keys():
			self.__user_metadata_entries.append( ('OCCULTATION-OBJECT-NAME',		RavfMetadataType.UTF8STRING,	self.metadata['occultationObjectName']) )

		if 'occultationStar' in self.metadata.keys():
			self.__user_metadata_entries.append( ('OCCULTATION-STAR',			RavfMetadataType.UTF8STRING,	self.metadata['occultationStar']) )

		if 'instrumentAperture' in self.metadata.keys():
			self.__user_metadata_entries.append( ('INSTRUMENT-APERTURE',			RavfMetadataType.UINT16,	self.metadata['instrumentAperture']) )

		if 'instrumentOpticalType' in self.metadata.keys():
			self.__user_metadata_entries.append( ('INSTRUMENT-OPTICAL-TYPE',		RavfMetadataType.UTF8STRING,	self.metadata['instrumentOpticalType']) )

		self.logger.info('Width: %d' % self.width)
		self.logger.info('Height: %d' % self.height)
		self.logger.info('Stride: %d' % self.stride)

		buffer_size = self.stride * self.height

		self.framewriter = FrameWriter.getInstance()
		self.framewriter.createSharedMemory(buffer_size)
		self.framewriter.startRecordingVideo(self.filename, self.__required_metadata_entries, self.__user_metadata_entries)


	def stop(self):
		self.recording = False
		self.logger.info('finished(stopped) ravf_encoder')
		# self._advwriter.add_user_metadata_tag(name = 'my name', value = 'my value')

		# stop closes the file
		super().stop()
		self.otestamper.stopRecordingVideo()
		now = datetime.utcnow()
		self.stop_observing_time = (now.hour, now.minute, float(now.second) + (now.microsecond/1000000.0))
		self.otestamper.startUpdateStatusTimer()
		self.framewriter.stopRecordingVideo()
		self.logger.info(self.otestamper.statistics)
		self.processLogger.queue.put( { 'cmd': 'revert' } )	# Revert back to astrid.log for logging
		self.logger.info('switching back to astrid.log')
		self.processLogger.setPropagate(True)			# Switch progation to the default logger back on
		if self.metadata['naReportForm'] is not None:
			self.camera.statusMsg('Updating xlsx')
			FillInNAReport(self.metadata['naReportForm'], self.__required_metadata_entries, self.__user_metadata_entries, self.start_observing_time, self.stop_observing_time)
		self.camera.statusMsg('Recording Finished')


	def exposureNsMatchesFrameDuration(self, exposure_ns, frameDurationMicros):
		if exposure_ns == 0:
			return False
	
		delta = abs(((frameDurationMicros * 1000) - exposure_ns) / exposure_ns)
		#self.logger.debug('exposureNsMatchesFrameDuration: %dns %dns %0.3f' % (exposure_ns, frameDurationMicros * 1000, delta))
		if delta < 0.1:
			return True
		return False



	def eatFrameInfosTillStart(self):
		# Eat all the frameInfos from OTEStamper until we see the halfFrameDuration and the transition back to the wholeFrameDuration
		state = 0

		while True:
			if not self.otestamper.getFrameInfo():
				self.otestamper.statistics['otestamper_comms_failed'] += 1
			else:
				halfDurationMicros = max(self.frameHalfDurationMicros, RavfEncoder.MINIMUM_FRAME_DURATION_MICROS)

				if state == 0 and self.exposureNsMatchesFrameDuration(self.otestamper.frameInfo['frameDuration'], halfDurationMicros):
					state = 1
				elif state == 1 and self.exposureNsMatchesFrameDuration(self.otestamper.frameInfo['frameDuration'], self.metadata['frameDurationMicros']):
					break


	def _encode(self, stream, request):
		now = datetime.utcnow()

		if not self.recording:
			return 

		metadata		= request.get_metadata()
		fb			= request.request.buffers[stream]
		exposure_duration_ns	= metadata['ExposureTime'] * 1000

		self.logger.debug('exposure_duration_ns: %d' % exposure_duration_ns)

		if self.syncState > 1:
			self.waiting_frame_count -= 1

		# We need to sync the otestamper frames to the video frames we receive here
		# To do that, we half the frame rate of the camera and look for that change from OTEStamper
		# This finite state machine handles that
		self.logger.debug('syncState: %d' % self.syncState)
		if self.syncState == 0:
			self.camera.ui.waitingToSyncMessageBoxStart()
			# Initial state, we tell the camera to half the frame rate
			self.camera.configureVideoFrameDuration(self.frameHalfDurationMicros)
			self.syncState = 1
			return
		elif self.syncState == 1:
			# We now set back to the original rate and wait for the half rate to appear
			self.camera.configureVideoFrameDuration(self.metadata['frameDurationMicros'])
			if self.exposureNsMatchesFrameDuration(exposure_duration_ns, self.frameHalfDurationMicros):
				self.syncState = 3
			else:
				self.syncState = 2
			return
		elif self.syncState == 2:
			# We wait for the half rate to appear in the video stream
			self.camera.ui.waitingToSyncMessageBoxUpdateCount(self.waiting_frame_count)
			if self.exposureNsMatchesFrameDuration(exposure_duration_ns, self.frameHalfDurationMicros):
				self.syncState = 3
			return
		elif self.syncState == 3:
			# We now wait for the original rate to appear in the video stream
			self.camera.ui.waitingToSyncMessageBoxUpdateCount(self.waiting_frame_count)
			if self.exposureNsMatchesFrameDuration(exposure_duration_ns, self.metadata['frameDurationMicros']):
				self.syncState = 4
				self.eatFrameInfosTillStart()
				self.camera.statusMsg('Frame Sync Achieved, Recording started')
				self.camera.ui.waitingToSyncMessageBoxDone()
			else:
				return
		else:
			if not self.otestamper.getFrameInfo():
				self.otestamper.statistics['otestamper_comms_failed'] += 1
				return

		sequence		= self.otestamper.frameInfo['frameSequence']
		start_timestamp_ns	= self.otestamper.frameInfo['frameEndNanoSecondsSince2010'] - exposure_duration_ns

		# Identify dropped frames from the camera
		if not self.firstFrame:
			camera_timestamp_delta = fb.metadata.timestamp - self.lastCameraTimestamp
			if camera_timestamp_delta > (1.5 * self.metadata['shutter_ns']):
				numFramesDropped = round(camera_timestamp_delta / self.metadata['shutter_ns']) - 1
				self.otestamper.statistics['dropped_camera'] += abs(numFramesDropped)
				self.logger.warning('camera frames dropped: %d' % numFramesDropped)
				self.logger.warning('fbTimestamp:%d lastCameraTimestamp:%d Delta: %d' % (fb.metadata.timestamp, self.lastCameraTimestamp, camera_timestamp_delta))

				for i in range(numFramesDropped):
					if not self.otestamper.getFrameInfo():
						self.otestamper.statistics['otestamper_comms_failed'] += 1
						self.logger.critical('attempted to force otestamper to ignore 1 frame, but comms failed, FRAMES COULD BE OUT OF SYNC!')
					self.logger.warning('forced otestamper to ignore 1 frame')
		self.lastCameraTimestamp = fb.metadata.timestamp

		delayedDeltaMicroseconds = (now - self.otestamper.frameInfo['frameEndDateTime']).microseconds	
		self.logger.debug('frame data with timestamp end %s sent to framewriter process at %s (delta: %dus)' % (self.otestamper.frameInfo['frameEndDateTime'].strftime('%Y-%m-%dT%H:%M:%S.%f'), now.strftime('%Y-%m-%dT%H:%M:%S.%f'), delayedDeltaMicroseconds))

		# Check the time between frames isn't too much and incremenet badFrameDelta if it is
		diffTimestamp	     = (start_timestamp_ns - self.lastTimeFrame)
		diffTimestampPercent = diffTimestamp / float(exposure_duration_ns)
		if not self.firstFrame and (diffTimestampPercent > 1.05 or diffTimestampPercent < 0.95):
			self.otestamper.statistics['badFrameDelta'] += 1
			self.logger.warning("start_timestamp_ns: %dns" % start_timestamp_ns)
			self.logger.warning("self.lastTimeFrame: %dns" % self.lastTimeFrame)
			self.logger.warning("frame time delta too Large: %dns" % diffTimestamp)
			start_timestamp_ns = self.lastTimeFrame + exposure_duration_ns
			self.logger.critical("reconstructed start_timestampe_ns as: %dns" % start_timestamp_ns)
		self.lastTimeFrame = start_timestamp_ns


		# Identify dropped frames from OTEStamper
		# If frame sequence numbers are not consecutive, then frames have been dropped
		sequenceDiff = (sequence + 256 - self.lastSequence) % 256
		if not self.firstFrame and sequenceDiff != 1:
			self.otestamper.statistics['dropped_otestamper'] += 1
			self.logger.critical('dropped: %d frames' % (sequenceDiff - 1))


		# If the capture clock has excessive drift, this is due to an error likely due to load in OTEStamper
		if self.otestamper.frameInfo['errorCaptureClockSystemDrift'] > 0:
			self.otestamper.statistics['badClockDrift'] += 1
			self.logger.critical('badClockDrift from otestamper')

		if self.otestamper.frameInfo['errorSequence'] > 0:
			self.otestamper.statistics['sequence'] += 1
			self.logger.critical('bad frame sequence from otestamper')

		if self.otestamper.frameInfo['errorEndDateTime'] > 0:
			self.otestamper.statistics['endDateTime'] += 1
			self.logger.critical('frame end date/time is older than previous frame')

		if self.otestamper.frameInfo['errorClockStatus'] > 0:
			self.otestamper.statistics['clockStatus'] += 1
			self.logger.warning('Clock Status != 0x07 or 0x0B from OTEStamper')


		self.firstFrame = False
		self.lastSequence = sequence

		# Map the buffer to b, and outpout the frame
		with _MappedBuffer(request, request.picam2.encode_stream_name) as b:
			self.outputframe(b, timestamp=start_timestamp_ns, exposure_duration_ns = exposure_duration_ns, sequence = sequence)


	# Outputs a frame to ravf

	def outputframe(self, frame, timestamp: int, exposure_duration_ns: int, sequence: int):
		if self.recording:
			metadata = {	'frame_type': RavfFrameType.LIGHT,
					'start_timestamp': timestamp,
					'exposure_duration': exposure_duration_ns,
					'satellites': self.otestamper.status['numSatellites'],
					'almanac_status': self.otestamper.status['clockStatus'],
					'almanac_offset': self.otestamper.status['leapSeconds'],
					'satellite_fix_status': self.otestamper.status['fix'],
					'sequence': sequence
				}
			self.framewriter.writeFrame(frame, metadata)
			self.logger.debug('frame length: %d' % len(frame))
