from UiPanel import UiPanel



class UiPanelDisplay2(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 2')

		self.camera = camera
		self.widgetExpAnalysis	= self.addButton('Exposure Analysis')


	def registerCallbacks(self):
		self.widgetExpAnalysis.clicked.connect(self.buttonExpAnalysis)
		


	# CALLBACKS

	def buttonExpAnalysis(self):
		self.camera.annotationStars = None
		self.camera.updateDisplayOptions()
		self.camera.ui.panelTask.buttonPlateSolvePressed(True, expAnalysis = True)
       

	# OPERATIONS
