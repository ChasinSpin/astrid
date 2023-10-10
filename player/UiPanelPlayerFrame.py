from astutils import AstUtils
from UiPanel import UiPanel
#from PyQt5.QtCore import Qt
#from PyQt5.QtWidgets import QMessageBox


class UiPanelPlayerFrame(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, args = None):
		super().__init__('Video Frame')
		
		self.widgetLastFrame		= self.addOpencv(args['width'], args['height'])
		self.widgetControls		= self.addPlayerControls(args['callback_firstFrame'], args['callback_lastFrame'], args['callback_prevFrame'], args['callback_nextFrame'], args['callback_togglePlay'], args['callback_setFrameNum'])

		#self.setColumnWidth(1, 140)


	def registerCallbacks(self):
		pass
		#self.widgetHome.clicked.connect(self.buttonHomePressed)
		#self.widgetTrackingRate.currentTextChanged.connect(self.comboBoxTrackingRateChanged)


	# CALLBACKS

	#def buttonHomePressed(self):
	#	if self.settings['parkmethod'] == 'home':
	#		self.camera.indi.telescope.goHome()
	#	else:
	#		self.camera.togglePark()


	# OPERATIONS

	#def messageBoxNoPlateSolve(self):
	#	QMessageBox.warning(self, ' ', 'Plate solve last photo before syncing.', QMessageBox.Ok)
