from UiPanel import UiPanel



class UiPanelDisplay1(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 1')

		self.camera = camera
		self.widgetAutoStretch		= self.addCheckBox('Stretch')
		self.widgetAutoStretchLower	= self.addLineEditDouble('Stretch Lower', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchUpper	= self.addLineEditDouble('Stretch Upper', 0.0, 255.0, 1, editable=True)
		self.widgetZebras		= self.addCheckBox('Zebras')
		#self.widgetCrosshairs		= self.addCheckBox('Center Marker')
		self.widgetObjectTarget		= self.addCheckBox('Object Target')
		self.widgetStarDetection	= self.addCheckBox('Star Detect <=0.5fps')

		self.widgetObjectTarget.setChecked(True)
		self.widgetAutoStretchLower.setText('%0.1f' % self.camera.autoStretchLower)
		self.widgetAutoStretchUpper.setText('%0.1f' % self.camera.autoStretchUpper)


	def registerCallbacks(self):
		self.widgetAutoStretch.stateChanged.connect(self.checkBoxAutoStretchChanged)
		self.widgetAutoStretchLower.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetAutoStretchUpper.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetZebras.stateChanged.connect(self.checkBoxZebrasChanged)
		#self.widgetCrosshairs.stateChanged.connect(self.checkBoxCrosshairsChanged)
		self.widgetObjectTarget.stateChanged.connect(self.checkBoxObjectTargetChanged)
		self.widgetStarDetection.stateChanged.connect(self.checkBoxStarDetectionChanged)


	# CALLBACKS

	def checkBoxAutoStretchChanged(self):
		state = self.widgetAutoStretch.checkState()
		aState = False
		if state == 2:
			aState = True
		self.camera.setAutoStretch(aState)


	def checkBoxZebrasChanged(self):
		state = self.widgetZebras.checkState()
		zState = False
		if state == 2:
			zState = True
		self.camera.setZebras(zState)


	#def checkBoxCrosshairsChanged(self, checked):
	#	state = self.widgetCrosshairs.checkState()
	#	cState = False
	#	if state == 2:
	#		cState = True
	#	self.camera.setCrossHairs(cState)


	def checkBoxObjectTargetChanged(self, checked):
		state = self.widgetObjectTarget.checkState()
		cState = False
		if state == 2:
			cState = True
		self.camera.setObjectTarget(cState)


	def checkBoxStarDetectionChanged(self, checked):
		state = self.widgetStarDetection.checkState()
		cState = False
		if state == 2:
			cState = True
		self.camera.setStarDetection(cState)


	def lineEditAutoStretchLimitsChanged(self):
		lower = float(self.widgetAutoStretchLower.text())
		upper = float(self.widgetAutoStretchUpper.text())
		self.camera.setAutoStretchLimits(lower, upper)


	# OPERATIONS
