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

	def __init__(self, windowTitle, astrid_drive, loadRavf_callback, width, height, callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame, callback_togglePlay, callback_setFrameNum):
		super(UiPlayer, self).__init__()

		# Create the panels
		self.panelFrame		= UiPanelPlayerFrame(args = {'width': width, 'height': height, 'callback_firstFrame': callback_firstFrame, 'callback_lastFrame': callback_lastFrame, 'callback_prevFrame': callback_prevFrame, 'callback_nextFrame': callback_nextFrame, 'callback_togglePlay': callback_togglePlay, 'callback_setFrameNum': callback_setFrameNum})
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


	# Shows msg in the status bar

	def showStatusMessage(self, msg):
		self.statusBar().showMessage(msg)


	# Connects up all the callbacks for the UI

	def registerCallbacks(self):
		self.panelFrame.registerCallbacks()
		self.panelOperations.registerCallbacks()
