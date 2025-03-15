import os
import subprocess
from UiPanel import UiPanel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout
from UiQDialog import UiQDialog
from settings import Settings
from StarCatalogExtract import StarCatalogExtract



class UiPanelDisplay2(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 2')

		self.camera = camera
		self.widgetExpAnalysis	= self.addButton('Exposure Analysis')
		self.widgetFocuser	= self.addButton('Focuser')

		self.settingsFocus	= Settings.getInstance().focus
		self.focuserSpeed	= self.settingsFocus['coarse_step']


	def registerCallbacks(self):
		self.widgetExpAnalysis.clicked.connect(self.buttonExpAnalysis)
		self.widgetFocuser.clicked.connect(self.buttonFocuser)
		


	# CALLBACKS

	def buttonExpAnalysis(self):
		self.camera.annotationStars = None
		self.camera.updateDisplayOptions()

		starCatalogExtract = StarCatalogExtract()
		if starCatalogExtract.checkAndExtract():
			self.camera.ui.panelTask.buttonPlateSolvePressed(True, expAnalysis = True)


	def buttonFocuser(self):
		self.camera.annotationStars = None
		self.camera.updateDisplayOptions()

		self.focuserDialog = UiQDialog(parent = self.camera.ui, topLeft = (260, 20))
		self.focuserDialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)

		self.focuserDialog.plateSolvePanel = UiPanel('Focuser')
		self.panel = self.focuserDialog.plateSolvePanel
		if self.settingsFocus['indi_module'] == 'indi_simulator_focus':
			self.panel.addLabel('Simulated Focuser (see focus settings)')
			self.panel.addSpacer()
			
		self.panel.moveToPosition	= self.panel.addLineEditInt('Move To Position', 0, 60000)
		self.panel.currentPosition	= self.panel.addLineEditInt('Set Current Position', 0, 60000)
		self.panel.focuser		= self.panel.addFocuser(self.buttonUpPressed, self.buttonDownPressed, self.buttonSpeedChanged)

		if self.settingsFocus['has_temperature']:
			self.panel.temperature	= self.panel.addLineEditDouble('Temperature', -200, 200, 2, editable = False)

		self.panel.moveToPosition.setText(str(int(self.camera.lastFocuserPosition)))
		self.focuserPositionUpdateDisplay(self.camera.lastFocuserPosition)
		if self.settingsFocus['has_temperature']:
			self.focuserTemperatureUpdateDisplay(self.camera.lastFocuserTemperature)

		# Setup Focuser and Temperature Camera Callbacks
		self.camera.focuserPositionDialogCallback = self.focuserPositionUpdateDisplay
		if self.settingsFocus['has_temperature']:
			self.camera.focuserTemperatureDialogCallback = self.focuserTemperatureUpdateDisplay

		self.panel.stop	= self.panel.addButton('Stop Movement')
		self.panel.cancel	= self.panel.addButton('Cancel')

		# Setup Callbacks
		self.panel.stop.clicked.connect(self.buttonFocuserStopPressed)
		self.panel.cancel.clicked.connect(self.buttonFocuserCancelPressed)
		self.panel.moveToPosition.editingFinished.connect(self.moveToPositionChanged)
		self.panel.currentPosition.editingFinished.connect(self.currentPositionChanged)

		self.focuserDialogLayout = QVBoxLayout()
		self.focuserDialogLayout.addWidget(self.panel)
		self.focuserDialog.setLayout(self.focuserDialogLayout)
		self.focuserDialog.exec()


	# OPERATIONS

	def moveToPositionChanged(self):
		self.camera.indi.focuser.moveToPosition(int(self.panel.moveToPosition.text()))


	def currentPositionChanged(self):
		newPosition = int(self.panel.currentPosition.text())

		# Position hasn't changed, so we return
		if newPosition == int(self.camera.lastFocuserPosition):
			return

		if QMessageBox.question(self.panel, ' ', 'You have requested to change the current position of the focuser, this will cause a loss of relative position.\n\nDo you wish to continue?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
			self.camera.indi.focuser.setCurrentPosition(newPosition)
		else:
			self.focuserPositionUpdateDisplay(self.camera.lastFocuserPosition)


	def buttonFocuserStopPressed(self):
		self.camera.indi.focuser.abortMove()


	def buttonFocuserCancelPressed(self):
		if self.focuserDialog is not None:
			self.camera.indi.focuser.abortMove()
			self.camera.focuserPositionDialogCallback = None
			self.camera.focuserTemperatureDialogCallback = None
			self.focuserDialog.reject()
			self.focuserDialog = None


	def buttonUpPressed(self):
		print('Up')
		self.camera.indi.focuser.moveToPosition(int(self.camera.lastFocuserPosition) + self.focuserSpeed)


	def buttonDownPressed(self):
		print('Down')
		self.camera.indi.focuser.moveToPosition(int(self.camera.lastFocuserPosition) - self.focuserSpeed)
		


	def buttonSpeedChanged(self, speed):
		print('Speed:', speed)
		if speed == 'Coarse':
			self.focuserSpeed = self.settingsFocus['coarse_step']
		else:
			self.focuserSpeed = self.settingsFocus['fine_step']


	def focuserPositionUpdateDisplay(self, position):
		self.panel.currentPosition.setText(str(int(position)))


	def focuserTemperatureUpdateDisplay(self, temperature):
		self.panel.temperature.setText(str(temperature))
