from processlogger import ProcessLogger
import json
from PyQt5.QtCore import QTimer
from UiStatusButton import UiStatusButton
from astsite import AstSite
from datetime import datetime, timedelta
import multiprocessing
import queue    # imported for using queue.Empty exception
import time
from processotestamper import ProcessOteStamper
import threading
from settings import Settings



# Singleton

class OteStamper:

	__instance = None

	DELTA_SYSTEM_TIME_SECS_MAX = 30


	def __init__(self):
		if OteStamper.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			OteStamper.__instance = self

			self.logger = ProcessLogger.getInstance().getLogger()

			self.logger.info('OTEStamper: Number of cpus: %d' % multiprocessing.cpu_count())

			self.ui = None
		
			self.callback = None

			# Setup ProcessOteStamper as a seperate process
			self.queue_frameInfo	= multiprocessing.Queue()		# This is incoming from ProcessOteStamper to OteStamper and contains the frame info
			self.queue_gpsInfo	= multiprocessing.Queue()		# This is incoming from the ProcessOteStamper to OteStamper and contains status and gps info
			self.queue_cmd		= multiprocessing.Queue()		# This is outgoing, from OteStamper to ProcessOteStamper and allows commands to be sent to the ProcessOteStamper process

			self.processOteStamper	= ProcessOteStamper()
			self.process = multiprocessing.Process(target=self.processOteStamper.main, args=(ProcessLogger.getInstance().queue, self.queue_frameInfo, self.queue_gpsInfo, self.queue_cmd))
			self.process.start()

			self.status = None

			self.frameInfo = None

			self.resetStatistics()

			self.updateStatusTimer = QTimer()
			self.updateStatusTimer.timeout.connect(self.__updateStatusTimer)
			self.updateStatusTimer.setInterval(500)
			self.startUpdateStatusTimer()


	@staticmethod
	def getInstance():
		if OteStamper.__instance == None:
			if (threading.current_thread() is threading.main_thread()) and multiprocessing.current_process().name == 'main':
				OteStamper()
			else:
				raise ValueError('otestamper: not called from main thread/process')

		return OteStamper.__instance


	def checkMainThreadProcess(self):
		if not ((threading.current_thread() is threading.main_thread()) and multiprocessing.current_process().name == 'main'):
			raise ValueError('otestamper: not called from main thread/process')


	def terminate(self):
		"""
                        Call once from the top process to stop the logging process and terminate the logging process
                """
		self.checkMainThreadProcess()
		self.queue_cmd.put('terminate')
		self.process.join()


	"""
	Gets the frame information from OTEStamper
	Returns: Dictionary(leapSeconds, clockStatus, unixEpoch, frameSequence)

	"""
	def getFrameInfo(self) -> bool:
		self.checkMainThreadProcess()
		try:
			self.frameInfo = self.queue_frameInfo.get_nowait()
			if self.frameInfo is None:
				self.logger.critical('getFrameInfo received no data from ProcessOteStamper on queue_frameInfo')
				self.statistics['getFrameInfoNoData'] += 1
			else:
				self.logger.debug('received frame info from ProcessOteStamper on queue_frameInfo: %s' % self.frameInfo)
		except queue.Empty:
			self.frameInfo = None
			self.logger.critical('getFrameInfo, ready to write a frame, but no frame info available from ProcessOteStamper on queue_frameInfo')
			self.statistics['getFrameInfoNotReady'] += 1
			return False
		else:
			self.__updateStatusButtons()
			return True


	def __updateStatusTimer(self):
		"""
			Note: This queries the OTEStamper board for status, however a get_nowait is used on the queue
			This means that as it is executed by another process, the information returned maybe upto
			1 second later.  This isn't of primary concern as it only impacts the information presented to the user
			via the UI, and that is preferrable of adding delays to allow for the processing and subsequently delaying
			this execution
		"""
		self.checkMainThreadProcess()

		# This is asynchronous, we pull off the last request first, and issue the new request

		try:
			self.status = self.queue_gpsInfo.get_nowait()
			if self.callback is not None:
				self.callback(self.status)
		except queue.Empty:
			self.queue_cmd.put('gpsinfo')
			return
		else:
			self.queue_cmd.put('gpsinfo')
			self.__updateStatusButtons()

		#print('Status:', self.status)


	def setUi(self, ui):
		self.ui = ui


	def __updateStatusButtons(self):
		if self.ui is None:
			return

		self.checkMainThreadProcess()
		if self.status == None:
			self.ui.panelStatus.widgetSite.setStatus(UiStatusButton.STATUS_UNKNOWN)
			self.ui.panelStatus.widgetGps.setStatus(UiStatusButton.STATUS_UNKNOWN)
			self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_UNKNOWN)
			self.ui.panelStatus.widgetAcquisition.setStatus(UiStatusButton.STATUS_UNKNOWN)
		else:
			if self.ui.panelStatus:
				if self.status['fix'] < 2 or AstSite.distanceFromGps(self.status['latitude'], self.status['longitude']) >= 50.0:
					self.ui.panelStatus.widgetSite.setStatus(UiStatusButton.STATUS_POOR)
				elif self.status['fix'] == 2 or self.status['pdop'] > 5.0 or self.status['hdop'] > 5.0 or self.status['vdop'] > 5.0 or AstSite.distanceFromGps(self.status['latitude'], self.status['longitude']) >= 15.0:
					self.ui.panelStatus.widgetSite.setStatus(UiStatusButton.STATUS_ADEQUATE)
				elif self.status['fix'] == 3:
					self.ui.panelStatus.widgetSite.setStatus(UiStatusButton.STATUS_GOOD)

				if self.status['fix'] < 2:
					self.ui.panelStatus.widgetGps.setStatus(UiStatusButton.STATUS_POOR)
				elif self.status['fix'] == 2 or self.status['numSatellites'] < 5:
					self.ui.panelStatus.widgetGps.setStatus(UiStatusButton.STATUS_ADEQUATE)
				elif self.status['fix'] == 3:
					self.ui.panelStatus.widgetGps.setStatus(UiStatusButton.STATUS_GOOD)

				deltaSystemTimeSecs = abs(self.status['deltaSystemTimeSecs'])
				if (self.status['clockStatus'] & 0x03) == 0x03:
					if (self.status['clockStatus'] & 0x10) == 0x10:
						if deltaSystemTimeSecs >= self.DELTA_SYSTEM_TIME_SECS_MAX:
							self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_POOR)
						else:
							self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_ADEQUATE)
					elif ((self.status['clockStatus'] & 0x04) == 0x04) or ((self.status['clockStatus'] & 0x08) == 0x08):
						if deltaSystemTimeSecs >= self.DELTA_SYSTEM_TIME_SECS_MAX:
							self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_POOR)
						else:
							self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_GOOD)
					else:
						self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_POOR)
				else:
					self.ui.panelStatus.widgetTiming.setStatus(UiStatusButton.STATUS_POOR)


				badStats = False
				for key in self.statistics.keys():
					if self.statistics[key] > 0:
						badStats = True
						break
				if badStats:
					self.ui.panelStatus.widgetAcquisition.setStatus(UiStatusButton.STATUS_POOR)
				else:
					self.ui.panelStatus.widgetAcquisition.setStatus(UiStatusButton.STATUS_GOOD)

		self.ui.panelStatus.updateStatusLabel()


	def startRecordingVideo(self):
		self.checkMainThreadProcess()
		self.queue_cmd.put('startRecording')


	def stopRecordingVideo(self):
		self.checkMainThreadProcess()
		self.queue_cmd.put('stopRecording')


	def startUpdateStatusTimer(self):
		self.checkMainThreadProcess()
		self.updateStatusTimer.start()


	def stopUpdateStatusTimer(self):
		self.checkMainThreadProcess()
		self.updateStatusTimer.stop()


	def resetStatistics(self):
		self.checkMainThreadProcess()
		self.statistics = { 'dropped_camera': 0, 'dropped_otestamper': 0, 'otestamper_comms_failed': 0, 'badClockDrift': 0, 'badFrameDelta': 0, 'getFrameInfoNoData': 0, 'getFrameInfoNotReady': 0, 'finalFrameNotWritten': 0, 'sequence': 0, 'endDateTime': 0, 'clockStatus': 0}


	def buzzerEnabled(self, enable):
		self.checkMainThreadProcess()
		self.queue_cmd.put('buzzer %s' % ('on' if enable else 'off'))


	def fanEnabled(self, enable):
		self.checkMainThreadProcess()
		self.queue_cmd.put('fan %s' % ('on' if enable else 'off'))


	def setGpsTimeCallback(self, callback):
		self.callback = callback


	def fuzzGps(self):
		self.checkMainThreadProcess()
		self.queue_cmd.put('fuzz gps')
