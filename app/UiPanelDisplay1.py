from UiPanel import UiPanel
from settings import Settings



class UiPanelDisplay1(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 1')

		self.camera = camera

		self.stretchOptions		= [ 'None', 'Histogram Equalization', 'CLAHE ClipLimit=0.0', 'CLAHE ClipLimit=1.0', 'CLAHE ClipLimit=4.0', 'CLAHE ClipLimit=8.0', 'CLAHE ClipLimit=16.0', 'CLAHE ClipLimit=32.0', 'CLAHE ClipLimit=64.0', 'CLAHE ClipLimit=128.0', 'MinMax (15,30)',       'MinMax (15,100)',        'MinMax (5,30)',        'MinMax (Custom)'            ]
		self.stretchSettings		= [  None,  ['histEq'],               ['clahe', 0.0],        ['clahe', 1.0],        ['clahe', 4.0],        ['clahe', 8.0],        ['clahe', 16.0],        ['clahe', 32.0],        ['clahe', 64.0],        ['clahe', 128.0],        ['minmax', 15.0, 30.0], ['minmax', 15.0, 100.0],  ['minmax', 5.0, 30.0],  ['minmaxcustom', 15.0, 30.0] ]
		self.widgetStretch		= self.addComboBox('Stretch', self.stretchOptions)
		self.widgetStretch.setObjectName('comboBoxStretch')

		self.widgetAutoStretchLower	= self.addLineEditDouble('Stretch Lower', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchUpper	= self.addLineEditDouble('Stretch Upper', 0.0, 255.0, 1, editable=True)
		self.widgetAutoStretchLower.setText('15.0')	# This comes from the black level offset in the datasheet (60) divided by 4 (10 bit to 8 bit conversion)
		self.widgetAutoStretchUpper.setText('30.0')


		stretch_method = Settings.getInstance().hidden['stretch_method']
		if stretch_method >= len(self.stretchOptions):
			stretch_method = 0

		defaultStretchOption = self.stretchOptions[stretch_method]
		self.widgetStretch.setCurrentText(defaultStretchOption)
		self.comboBoxStretchChanged(defaultStretchOption)

		self.widgetZebras		= self.addCheckBox('Zebras')
		#self.widgetCrosshairs		= self.addCheckBox('Center Marker')
		self.widgetObjectTarget		= self.addCheckBox('Object Target')
		self.widgetStarDetection	= self.addCheckBox('Star Detect <=0.5fps')

		self.widgetObjectTarget.setChecked(True)


	def registerCallbacks(self):
		self.widgetStretch.currentTextChanged.connect(self.comboBoxStretchChanged)
		self.widgetAutoStretchLower.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetAutoStretchUpper.editingFinished.connect(self.lineEditAutoStretchLimitsChanged)
		self.widgetZebras.stateChanged.connect(self.checkBoxZebrasChanged)
		#self.widgetCrosshairs.stateChanged.connect(self.checkBoxCrosshairsChanged)
		self.widgetObjectTarget.stateChanged.connect(self.checkBoxObjectTargetChanged)
		self.widgetStarDetection.stateChanged.connect(self.checkBoxStarDetectionChanged)


	# CALLBACKS

	def comboBoxStretchChanged(self, text):
		ind = self.stretchOptions.index(text)
		self.updateMinMaxLimits(text)
		if self.stretchSettings[ind] is not None and self.stretchSettings[ind][0] == 'minmaxcustom':
			self.lineEditAutoStretchLimitsChanged()
		else:
		 	self.camera.setAutoStretch(self.stretchSettings[ind])

		Settings.getInstance().hidden['stretch_method'] = ind
		Settings.getInstance().writeSubsetting('hidden')


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
		self.camera.setAutoStretch(['minmaxcustom', lower, upper])


	# OPERATIONS

	def updateMinMaxLimits(self, text):
		if text == 'MinMax (Custom)':
			self.showWidget(self.widgetAutoStretchLower)
			self.showWidget(self.widgetAutoStretchUpper)
		else:
			self.hideWidget(self.widgetAutoStretchLower)
			self.hideWidget(self.widgetAutoStretchUpper)
