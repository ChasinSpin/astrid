import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QProgressBar
from CameraModel import OperatingMode
from UiPanel import UiPanel
from UiPanelTask import UiPanelTask
from UiPanelMount import UiPanelMount
from UiPanelObject import UiPanelObject
from UiPanelDisplay import UiPanelDisplay
from UiPanelStatus import UiPanelStatus
from settings import Settings



windowGeometry=(10, 100, 1200, 745)



class Ui(QtWidgets.QMainWindow):
	# Initializes and displays the UI

	def __init__(self, camera, windowTitle):
		super(Ui, self).__init__()

		self.camera = camera

		# Create the panels
		self.panelTask		= UiPanelTask(self.camera)
		self.panelObject	= UiPanelObject(self.camera)
		self.panelDisplay	= UiPanelDisplay(self.camera)
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
		centerPaneLayout = QVBoxLayout()
		centerPaneLayout.setSpacing(20)
		centerPaneLayout.addWidget(self.panelDisplay)
		centerPaneLayout.addWidget(camera.qt_picamera)
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
		self.setWindowTitle(windowTitle)
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
			self.camera.shutdown()
			
			os.system('sudo sh -c "/usr/bin/sync;/usr/bin/sync;/usr/bin/sync;/usr/bin/sleep 1;/usr/sbin/poweroff"')
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
		self.panelDisplay.registerCallbacks()
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
