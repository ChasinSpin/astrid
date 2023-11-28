from PlateSolver import *
from astutils import AstUtils
from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox, QFileDialog


class UiPanelPlayerOperations(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, args):
		super().__init__('Operations')

		self.astrid_drive	= args['astrid_drive']
		self.loadRavf_callback	= args['loadRavf_callback']

		self.widgetFileOpen	= self.addButton('Load Video')
		self.widgetPlateSolve	= self.addButton('Plate Solve')
		self.widgetSaveFrame	= self.addButton('Save Frame')
		self.widgetExportFits	= self.addButton('Export Fits Seq')

		self.widgetAutoStretch          = self.addCheckBox('Stretch')
		self.widgetAutoStretchLower     = self.addLineEditDouble('Stretch Lower', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchUpper     = self.addLineEditDouble('Stretch Upper', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchLower.setText('5')
		self.widgetAutoStretchUpper.setText('30')

		self.__setEnabledButtons(False)

		self.setFixedWidth(150)


	def registerCallbacks(self):
		self.widgetFileOpen.clicked.connect(self.buttonFileOpenPressed)
		self.widgetPlateSolve.clicked.connect(self.buttonPlateSolvePressed)
		self.widgetSaveFrame.clicked.connect(self.buttonSaveFramePressed)
		self.widgetExportFits.clicked.connect(self.buttonExportFitsPressed)
		self.widgetAutoStretch.stateChanged.connect(self.checkBoxAutoStretchChanged)
		self.widgetAutoStretchLower.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetAutoStretchUpper.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)

	# CALLBACKS

	def buttonFileOpenPressed(self):
		folder	= self.astrid_drive + '/OTEVideo'
		fname	= QFileDialog.getOpenFileName(self, 'Open file', folder, 'RAVF files (*.ravf)')[0]
		if len(fname) != 0:
			self.__setEnabledButtons(True)
			self.loadRavf_callback(fname)


	def buttonPlateSolvePressed(self):
		if self.widgetPlateSolve.text() == 'Plate Solve':
			self.plateSolveCallback()
			self.widgetPlateSolve.setText('Cancel')
		else:
			self.plateSolveCancelCallback()


	def buttonSaveFramePressed(self):
		self.saveFrameCallback()

	def buttonExportFitsPressed(self):
		self.exportFitsCallback()


	def checkBoxAutoStretchChanged(self):
		state = self.widgetAutoStretch.checkState()
		aState = False
		if state == 2:
			aState = True
		self.autoStretchCallback(aState)


	def lineEditAutoStretchLimitsChanged(self):
		lower = float(self.widgetAutoStretchLower.text())
		upper = float(self.widgetAutoStretchUpper.text())
		self.autoStretchLimitsCallback
		self.autoStretchLimitsCallback(lower, upper)


	# OPERATIONS

	def setCallbacks(self, autoStretchCallback, autoStretchLimitsCallback, plateSolveCallback, plateSolveCancelCallback, saveFrameCallback, exportFitsCallback):
		self.autoStretchCallback = autoStretchCallback
		self.autoStretchLimitsCallback = autoStretchLimitsCallback
		self.lineEditAutoStretchLimitsChanged()

		self.plateSolveCallback = plateSolveCallback
		self.saveFrameCallback = saveFrameCallback
		self.exportFitsCallback = exportFitsCallback
		self.plateSolveCancelCallback = plateSolveCancelCallback


	def plateSolveFinished(self):
		self.widgetPlateSolve.setText('Plate Solve')


	def __setEnabledButtons(self, enable):
		self.widgetPlateSolve.setEnabled(enable)
		self.widgetSaveFrame.setEnabled(enable)
		self.widgetExportFits.setEnabled(enable)
		self.widgetAutoStretch.setEnabled(enable)
		self.widgetAutoStretchLower.setEnabled(enable)
		self.widgetAutoStretchUpper.setEnabled(enable)
