import os
from settings import Settings
from UiPanel import UiPanel
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime, timedelta
from otestamper import OteStamper



class UiPanelAutoRecording(UiPanel):

	SHUTDOWN_SECONDS = 300

	# Initializes and displays a Panel

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.camera		= args['camera']
		self.start_time		= args['start_time']
		self.end_time		= args['end_time']
		self.event_time		= args['event_time']
		self.shutdown_time	= self.end_time + timedelta(seconds = UiPanelAutoRecording.SHUTDOWN_SECONDS)
		self.shutdown_required	= False
		self.camera.setPlannedAutoShutdown(self.shutdown_required)
		self.panel		= panel
		self.recording		= False

		self.widgetShutdown	= self.addCheckBox('Shutdown After Recording?')
		self.widgetStatus	= self.addTextBox('Updating...', height = 120)
		self.widgetCancel	= self.addButton('Stop Recording', True)

		self.state		= 0

		self.stateTimer = QTimer()
		self.stateTimer.timeout.connect(self.__doState)
		self.stateTimer.setInterval(500)
		self.stateTimer.start()

		

	def registerCallbacks(self):
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)
		self.widgetShutdown.stateChanged.connect(self.checkBoxShutdownChanged)


	def checkBoxShutdownChanged(self):
		state = self.widgetShutdown.checkState()
		sState = False
		if state == 2:
			sState = True
		self.shutdown_required = sState
		self.camera.setPlannedAutoShutdown(self.shutdown_required)


	
	# CALLBACKS

	def buttonCancelPressed(self):
		self.recordingCancel()
		self.panel.cancelDialog()


	# OPERATIONS

	def __doState(self):
		dt = datetime.utcnow()

		msg = None

		if   self.state == 0:
			# Waiting for start time
			if dt < self.start_time:
				deltaSecs = (self.start_time - dt).total_seconds()
				if deltaSecs > (5 * 60):
					delta = int(deltaSecs / 60)
					deltaText = 'minutes'
				else:
					delta = deltaSecs
					deltaText = 'seconds'
					
				msg = '%d %s until recording starts at %s'	% (delta, deltaText, self.start_time.strftime("%Y-%m-%dT%H:%M:%S"))
				if deltaSecs >= 1 and deltaSecs <= 6 and Settings.getInstance().camera['buzzer_enable']:
					OteStamper.getInstance().buzzerEnabled(True if int(deltaSecs) % 2 == 0 else False)
			else:
				msg = 'Starting Recording...'
				self.state += 1
				self.recordingStart()

		elif self.state == 1:
			# Recording
			elapsed = (dt - self.start_time).total_seconds()
			remaining = (self.end_time - dt).total_seconds()
			if dt <= self.event_time: 
				deltaEvent = (self.event_time - dt).total_seconds()
			else:
				deltaEvent = -(dt - self.event_time).total_seconds()
			msg = 'Recording:\n  elapsed %d seconds\n  remaining %d seconds\n  event in %d seconds'	% (elapsed, remaining, deltaEvent)

			if dt >= self.end_time:
				msg = 'Stopping Recording...'
				self.state += 1
				self.recordingFinish()

		elif self.state == 2:
			# Finished waiting shutdown
			if not self.shutdown_required:
				self.state += 1
				self.recordingCancel()
				self.panel.cancelDialog()
			else:
				if dt < self.shutdown_time:
					deltaSecs = (self.shutdown_time - dt).total_seconds()
					msg = 'Auto Shutdown In %d Seconds' % (deltaSecs)
				else:
					msg = 'Shutting down now...'
					self.shutdown()

		if msg is not None:
			self.widgetStatus.setText(msg)
		

	def recordingCancel(self):
		if self.recording:
			self.recordingFinish()
		self.stateTimer.stop()


	def recordingStart(self):
		self.recording = True
		
		# Re-enable tracking on scopes with tracking
		self.camera.indi.telescope.lockTrackingOff = False
		self.camera.indi.telescope.tracking(True)

		self.camera.ui.panelTask.widgetRecord.setChecked(True)
		self.camera.disableVideoFrameRateWarning = True
		self.camera.startRecording()
		self.camera.disableVideoFrameRateWarning = False


	def recordingFinish(self):
		self.camera.stopRecording()
		self.camera.ui.panelTask.widgetRecord.setChecked(False)
		self.camera.indi.telescope.tracking(False)
		self.recording = False

	def shutdown(self):
		self.stateTimer.stop()
		print('**** SHUTDOWN NOW ****')
		self.camera.shutdown()
		os.system('sudo sh -c "/usr/bin/sync;/usr/bin/sync;/usr/bin/sync;/usr/bin/sleep 1;/usr/sbin/poweroff"')
