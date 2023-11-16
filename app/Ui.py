from processlogger import ProcessLogger
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QMessageBox, QProgressBar
from CameraModel import OperatingMode
from UiPanel import UiPanel
from UiPanelTask import UiPanelTask
from UiPanelMount import UiPanelMount
from UiPanelObject import UiPanelObject
from UiPanelDisplay1 import UiPanelDisplay1
from UiPanelDisplay2 import UiPanelDisplay2
from UiPanelStatus import UiPanelStatus
from settings import Settings
from otestamper import OteStamper
from UiAutoCloseMessageBox import UiAutoCloseMessageBox



windowGeometry=(10, 100, 1200, 745)



class Ui(QtWidgets.QMainWindow):
	# Initializes and displays the UI

	def __init__(self, camera, windowTitle):
		super(Ui, self).__init__()

		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()

		self.camera			= camera
		self.windowTitle		= windowTitle
		self.disabledVoltageWarning	= False
		self.disabledVoltageShutdown	= False
		self.waitingToSync		= None

		# Create the panels
		self.panelTask		= UiPanelTask(self.camera)
		self.panelObject	= UiPanelObject(self.camera)
		self.panelDisplay1	= UiPanelDisplay1(self.camera)
		self.panelDisplay2	= UiPanelDisplay2(self.camera)
		self.panelMount		= UiPanelMount(self.camera)
		self.panelStatus	= UiPanelStatus(self.camera)

		# Assign panels to the left pane
		leftPaneLayout = QVBoxLayout()
		leftPaneLayout.setSpacing(20)
		leftPaneLayout.addWidget(self.panelTask)
		leftPaneLayout.addWidget(self.panelObject)

		# Create the left Pane
		self.leftPaneWidget = QWidget()
		self.leftPaneWidget.setLayout(leftPaneLayout)

		# Create the center Pane
		centerPaneLayout = QGridLayout()
		centerPaneLayout.setSpacing(20)

		centerPaneLayout.addWidget(self.panelDisplay1, 0, 0, 1, 1)
		centerPaneLayout.addWidget(self.panelDisplay2, 0, 1, 1, 1)
		centerPaneLayout.addWidget(camera.qt_picamera, 1, 0, 1, 2)
		camera.qt_picamera.setFixedSize(640,480)	
		camera.qt_picamera.setObjectName('cameraView')
		self.centerPaneWidget = QWidget()
		self.centerPaneWidget.setLayout(centerPaneLayout)

		# Assign panels to the right pane
		rightPaneLayout = QVBoxLayout()
		rightPaneLayout.setSpacing(20)
		rightPaneLayout.addWidget(self.panelMount)
		rightPaneLayout.addWidget(self.panelStatus)

		# Create the right Pane
		self.rightPaneWidget = QWidget()
		self.rightPaneWidget.setLayout(rightPaneLayout)

		# Create the window contents, which are:
		#    left pane, pi camera, right pane
		layout = QHBoxLayout()
		layout.addWidget(self.leftPaneWidget)
		layout.addWidget(self.centerPaneWidget)
		layout.addWidget(self.rightPaneWidget)

		# We need to encapsulate this layout in a widget
		self.mainLayoutWidget = QWidget()
		self.mainLayoutWidget.setLayout(layout)
		self.setCentralWidget(self.mainLayoutWidget)

		# Set the size and title of the window
		self.updateWindowTitle()
		self.setGeometry(windowGeometry[0], windowGeometry[1], windowGeometry[2], windowGeometry[3])

		# Add a progress bar to the status bar
		self.progressBar = QProgressBar()
		palette = self.progressBar.palette()
		palette.setColor(QPalette.Highlight, QColor('green'))
		#palette.setColor(QPalette.Highlight, QColor(0x88, 0x00, 0x00))
		self.progressBar.setPalette(palette)
		self.progressBar.setMaximumSize(250, 20)
		self.progressBar.setVisible(False)
		self.statusBar().addPermanentWidget(self.progressBar)

		# Register the callbacks
		self.registerCallbacks()

		# Update the UI to match the current mode
		self.update_ui_for_mode()

		# Set tracking
		settings_mount = Settings.getInstance().mount
		if settings_mount['tracking_capable']:
			self.panelMount.widgetTracking.setChecked(self.camera.indi.telescope.getTracking())
		if settings_mount['goto_capable'] and settings_mount['parkmethod'] == 'park':
			self.panelMount.widgetHome.setChecked(self.camera.indi.telescope.getPark())

		# Start meridian flip timer
		if Settings.getInstance().mount['align_axis'] == 'eq':
			self.panelMount.startMeridianFlipTimer()

		# Display the UI
		self.show()

		# Start the updateWindowTitleTimer (for voltage updates)
		self.updateWindowTitleTimer = QTimer()
		self.updateWindowTitleTimer.timeout.connect(self.updateWindowTitle)
		self.updateWindowTitleTimer.setInterval(5000)
		self.updateWindowTitleTimer.start()


	def shutdown_now(self):
		self.camera.shutdown()
		os.system('sudo sh -c "/usr/bin/sync;/usr/bin/sync;/usr/bin/sync;/usr/bin/sleep 1;/usr/sbin/poweroff"')


	# Called when the window is closed

	def closeEvent(self, event):
		if self.camera.isVideoRecording():
			QMessageBox.warning(self, ' ', 'Video is currently recording, stop recording before exiting Astrid.', QMessageBox.Ok)
			event.ignore()
			return

		msgBox = QMessageBox()
		msgBox.setWindowTitle('Exit Confirmation?')
		msgBox.setText('Exit Astrid?\n\nAlways remember to properly shutdown and wait 15 seconds\nbefore removing power to avoid SD Card corruption')
		msgBox.addButton(QMessageBox.Yes)
		msgBox.addButton('Shutdown', QMessageBox.YesRole)
		msgBox.addButton(QMessageBox.No)

		ret = msgBox.exec()

		if ret == QMessageBox.Yes:
			print('User exited program!')
			self.camera.shutdown()
			event.accept()
		elif ret == 0:
			print('User exited the program and shutdown!')
			self.shutdown_now()
			event.accept()
		else:
			event.ignore()


	# Updates the UI, hiding / showing buttons to match the current Camera Mode

	def update_ui_for_mode(self):
		opMode = self.camera.operatingMode
		self.panelTask.update_ui_for_mode(opMode)


	# Shows msg in the status bar

	def showStatusMessage(self, msg):
		self.statusBar().showMessage(msg)


	# Connects up all the callbacks for the UI

	def registerCallbacks(self):
		self.panelTask.registerCallbacks()
		self.panelObject.registerCallbacks()
		self.panelDisplay1.registerCallbacks()
		self.panelDisplay2.registerCallbacks()
		self.panelMount.registerCallbacks()
		self.panelStatus.registerCallbacks()


	def messageBoxPolarAlignTestModeWarning(self):
		QMessageBox.warning(self, ' ', 'Polar Alignment is in test mode and using previously recorded images. Disable polar_align_test in settings to use camera.', QMessageBox.Ok)


	def messageBoxPrepointTestModeWarning(self):
		QMessageBox.warning(self, ' ', 'Prepoint is in test mode and using previously recorded images. Disable polar_align_test in settings to use camera.', QMessageBox.Ok)


	def messageBoxVideoFileOverwriteQuestion(self, filename):
		QMessageBox.warning(self, ' ', 'File %s already exists, choose a different filename' % filename, QMessageBox.Ok)


	def messageBoxGotoNoObject(self):
		QMessageBox.warning(self, ' ', 'Unable to Goto Object as no object has been selected.', QMessageBox.Ok)


	def messageBoxTakeDark(self):
		QMessageBox.warning(self, ' ', 'Reminder: Record 100 frames of video with the lens cap on at the same fps/gain for dark noise reduction.', QMessageBox.Ok)


	def messageBoxDitherNoObject(self):
		QMessageBox.warning(self, ' ', 'An object has to be selected to dither. Switching dithering off.', QMessageBox.Ok)


	def indeterminateProgressBar(self, enable):
		if enable:
			self.progressBar.setRange(0, 0)
			self.progressBar.setValue(0)
		self.progressBar.setVisible(enable)


	def videoFrameRateWarning(self):
		# Returns True if the frame rate is too high to continue, otherwise False
		if self.camera.videoFrameDuration < int((1.0/60.0) * 1000000.0):
			QMessageBox.warning(self, ' ', 'Recording at frame rates above 60fps is not allowed!', QMessageBox.Ok)
			return True
		elif self.camera.videoFrameDuration < int((1.0/30.0) * 1000000.0):
			QMessageBox.warning(self, ' ', 'Recording at frame rates above 30fps is not recommended!', QMessageBox.Ok)
		return False


	def updateWindowTitle(self):
		otestamper	= OteStamper.getInstance()
	
		if otestamper.status is None:
			windowTitle = self.windowTitle
			voltage = 0.0
		else:
			voltage = otestamper.status['voltage']
			windowTitle = self.windowTitle + ' (%0.2f Volts)' % voltage 

		self.setWindowTitle(windowTitle)

		settings_general = Settings.getInstance().general

		if not self.disabledVoltageShutdown and settings_general['voltage_shutdown'] != 0 and voltage <= settings_general['voltage_shutdown'] and voltage != 0:
			msgBox = UiAutoCloseMessageBox()
			msgBox.setIcon(QMessageBox.Critical)
			shutdown_time = 20	# Seconds
			msg = 'Auto Shutdown in %ds due to Low Voltage: %0.2f V' % (shutdown_time, voltage)
			msgBox.setText(msg)
			msgBox.autoClose = shutdown_time * 1000
			msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

			self.logger.critical(msg)

			ret = msgBox.exec()
			if   ret == 0 or ret == QMessageBox.Ok:
				self.shutdown_now()
			elif ret == QMessageBox.Cancel:
				self.logger.critical('Shutdown due to low voltage cancelled')

			self.disabledVoltageShutdown = True

		if not self.disabledVoltageWarning and settings_general['voltage_warning'] != 0 and voltage <= settings_general['voltage_warning'] and voltage != 0:
			msg = 'Low Voltage: %0.2f V' % voltage
			QMessageBox.warning(self, ' ', msg, QMessageBox.Ok)
			self.logger.critical(msg)
			self.disabledVoltageWarning = True


	def waitingToSyncMessageBoxStart(self):
		if self.waitingToSync is not None:
			self.waitingToSyncMessageBoxDone()	

		self.waitingToSync = QMessageBox()
		self.waitingToSync.setIcon(QMessageBox.Information)
		self.waitingToSync.setStandardButtons(QMessageBox.Ok)
		self.waitingToSyncMessageBoxUpdateCount(12)
		self.waitingToSync.show()


	def waitingToSyncMessageBoxUpdateCount(self, count):
		msg = 'Waiting for Video Frame Sync To OTEStamper: %d' % count
		self.camera.statusMsg(msg)
		if self.waitingToSync is not None:
			self.waitingToSync.setText(msg)


	def waitingToSyncMessageBoxDone(self):
		self.waitingToSync.done(0)
		self.waitingToSync = None
