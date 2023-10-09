import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
#from PyQt5.QtWidgets import QMessageBox
#from UiPanel import UiPanel
from UiPanelPlayerFrame import UiPanelPlayerFrame
from UiPanelPlayerOperations import UiPanelPlayerOperations



windowGeometry=(10, 100, 1200, 745)



class UiPlayer(QtWidgets.QMainWindow):
	# Initializes and displays the UI

	def __init__(self, windowTitle, astrid_drive, loadRavf_callback, width, height, callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame):
		super(UiPlayer, self).__init__()

		# Create the panels
		self.panelFrame		= UiPanelPlayerFrame(args = {'width': width, 'height': height, 'callback_firstFrame': callback_firstFrame, 'callback_lastFrame': callback_lastFrame, 'callback_prevFrame': callback_prevFrame, 'callback_nextFrame': callback_nextFrame})
		self.panelOperations	= UiPanelPlayerOperations(args = {'astrid_drive': astrid_drive, 'loadRavf_callback': loadRavf_callback} )

		# Create the left Pane
		leftPaneLayout = QVBoxLayout()
		leftPaneLayout.setSpacing(20)
		leftPaneLayout.addWidget(self.panelFrame)

		# Create the left Pane
		self.leftPaneWidget = QWidget()
		self.leftPaneWidget.setLayout(leftPaneLayout)

		# Assign panels to the right pane
		rightPaneLayout = QVBoxLayout()
		rightPaneLayout.setSpacing(20)
		rightPaneLayout.addWidget(self.panelOperations)

		# Create the right Pane
		self.rightPaneWidget = QWidget()
		self.rightPaneWidget.setLayout(rightPaneLayout)
		self.rightPaneWidget.setFixedWidth(170)

		# Create the window contents, which are:
		#    left pane, right pane
		layout = QHBoxLayout()
		layout.addWidget(self.leftPaneWidget)
		layout.addWidget(self.rightPaneWidget)

		# We need to encapsulate this layout in a widget
		self.mainLayoutWidget = QWidget()
		self.mainLayoutWidget.setLayout(layout)
		self.setCentralWidget(self.mainLayoutWidget)

		# Set the size and title of the window
		self.setWindowTitle(windowTitle)
		self.setGeometry(windowGeometry[0], windowGeometry[1], windowGeometry[2], windowGeometry[3])

		# Register the callbacks
		self.registerCallbacks()

		# Update the UI to match the current mode
		#self.update_ui_for_mode()

		# Display the UI
		self.show()


	# Called when the window is closed

	def closeEvent(self, event):
		print('User exited program!')
		event.accept()


	# Updates the UI, hiding / showing buttons to match the current Camera Mode

	#def update_ui_for_mode(self):
	#	opMode = self.camera.operatingMode
	#	self.panelTask.update_ui_for_mode(opMode)


	# Shows msg in the status bar

	#def showStatusMessage(self, msg):
	#	self.statusBar().showMessage(msg)


	# Connects up all the callbacks for the UI

	def registerCallbacks(self):
		self.panelFrame.registerCallbacks()
		self.panelOperations.registerCallbacks()


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
