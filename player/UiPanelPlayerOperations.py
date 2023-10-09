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
		self.widgetExportFits	= self.addButton('Export Fits')

		self.setFixedWidth(150)


	def registerCallbacks(self):
		self.widgetFileOpen.clicked.connect(self.buttonFileOpenPressed)


	# CALLBACKS

	def buttonFileOpenPressed(self):
		folder	= self.astrid_drive + '/OTEVideo'
		fname	= QFileDialog.getOpenFileName(self, 'Open file', folder, 'RAVF files (*.ravf)')[0]
		if len(fname) != 0:
			self.loadRavf_callback(fname)


	#def buttonTrackingPressed(self):
	#	self.camera.indi.telescope.lockTrackingOff = False
	#	self.camera.toggleTracking()


	#def buttonAbortMotionPressed(self):
	#	self.camera.indi.telescope.abortMotion()


	#def comboBoxTrackingRateChanged(self, text):
	#	self.camera.indi.telescope.setTrackMode(text)


	# OPERATIONS

	#def messageBoxNoPlateSolve(self):
	#	QMessageBox.warning(self, ' ', 'Plate solve last photo before syncing.', QMessageBox.Ok)
