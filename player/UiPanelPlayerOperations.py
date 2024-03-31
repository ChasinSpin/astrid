from PlateSolver import *
from astutils import AstUtils
from UiPanel import UiPanel
from UiPanelMetadata import UiPanelMetadata

from PyQt5.QtWidgets import QFileDialog


class UiPanelPlayerOperations(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, args):
		super().__init__('Operations')

		self.astrid_drive	= args['astrid_drive']
		self.loadRavf_callback	= args['loadRavf_callback']

		self.widgetFileOpen	= self.addButton('Load Video')
		#self.widgetStackFrames  = self.addLineEditInt('Stack Frames', 1, 10, editable=True)
		self.widgetPlateSolve	= self.addButton('Plate Solve')
		self.widgetAnnotate	= self.addButton('Annotate')
		self.widgetSavePng	= self.addButton('Save Png Image')
		self.widgetSaveFits	= self.addButton('Save Fits Finder')
		self.widgetMetadata	= self.addButton('Metadata')
		self.widgetExportFits	= self.addButton('Export Fits Seq')

		self.widgetAutoStretch          = self.addCheckBox('Stretch')
		self.widgetAutoStretchLower     = self.addLineEditDouble('Stretch Lower', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchUpper     = self.addLineEditDouble('Stretch Upper', 0.0, 255.0, 1, editable=True)

		#self.widgetStackFrames.setText('1')
		self.widgetAutoStretchLower.setText('5')
		self.widgetAutoStretchUpper.setText('30')

		self.__setEnabledButtons(False)

		self.setFixedWidth(150)


	def registerCallbacks(self):
		self.widgetFileOpen.clicked.connect(self.buttonFileOpenPressed)
		#self.widgetStackFrames.editingFinished.connect(self.lineEditStackFramesChanged)
		self.widgetPlateSolve.clicked.connect(self.buttonPlateSolvePressed)
		self.widgetAnnotate.clicked.connect(self.buttonAnnotatePressed)
		self.widgetSavePng.clicked.connect(self.buttonSavePngPressed)
		self.widgetSaveFits.clicked.connect(self.buttonSaveFitsPressed)
		self.widgetMetadata.clicked.connect(self.buttonMetadataPressed)
		self.widgetExportFits.clicked.connect(self.buttonExportFitsPressed)
		self.widgetAutoStretch.stateChanged.connect(self.checkBoxAutoStretchChanged)
		self.widgetAutoStretchLower.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetAutoStretchUpper.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)

	# CALLBACKS

	def buttonFileOpenPressed(self):
		folder	= self.astrid_drive + '/OTEVideo'
		fname	= QFileDialog.getOpenFileName(self, 'Open file', folder, 'RAVF files (*.ravf)')[0]
		if len(fname) != 0:
			if self.loadRavf_callback(fname):
				self.__setEnabledButtons(True)
			else:
				self.__setEnabledButtons(False)

	def buttonPlateSolvePressed(self):
		if self.widgetPlateSolve.text() == 'Plate Solve':
			self.plateSolveCallback()
			self.widgetPlateSolve.setText('Cancel')
		else:
			self.plateSolveCancelCallback()


	def buttonAnnotatePressed(self):
		self.annotateCallback()


	def buttonSavePngPressed(self):
		self.savePngCallback()


	def buttonSaveFitsPressed(self):
		self.saveFitsCallback()


	def buttonMetadataPressed(self):
		dialog = UiDialogPanel('Metadata', UiPanelMetadata, args = {'metadata': self.metadataCallback()}, parent = self)


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


	def lineEditStackFramesChanged(self):
		stackFrames = int(self.widgetStackFrames.text())
		self.stackFramesCallback(stackFrames)



	# OPERATIONS

	def setCallbacks(self, autoStretchCallback, autoStretchLimitsCallback, plateSolveCallback, plateSolveCancelCallback, savePngCallback, saveFitsCallback, exportFitsCallback, metadataCallback, stackFramesCallback, annotateCallback):
		self.autoStretchCallback = autoStretchCallback
		self.autoStretchLimitsCallback = autoStretchLimitsCallback
		self.lineEditAutoStretchLimitsChanged()

		self.plateSolveCallback = plateSolveCallback
		self.savePngCallback = savePngCallback
		self.saveFitsCallback = saveFitsCallback
		self.exportFitsCallback = exportFitsCallback
		self.plateSolveCancelCallback = plateSolveCancelCallback
		self.metadataCallback = metadataCallback
		self.stackFramesCallback = stackFramesCallback
		self.annotateCallback = annotateCallback


	def plateSolveFinished(self):
		self.widgetPlateSolve.setText('Plate Solve')


	def __setEnabledButtons(self, enable):
		self.widgetPlateSolve.setEnabled(enable)
		self.widgetAnnotate.setEnabled(enable)
		#self.widgetStackFrames.setEnabled(enable)
		self.widgetSavePng.setEnabled(enable)
		self.widgetSaveFits.setEnabled(enable)
		self.widgetMetadata.setEnabled(enable)
		self.widgetExportFits.setEnabled(enable)
		self.widgetAutoStretch.setEnabled(enable)
		self.widgetAutoStretchLower.setEnabled(enable)
		self.widgetAutoStretchUpper.setEnabled(enable)
