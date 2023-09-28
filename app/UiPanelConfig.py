import os
import json
from UiPanel import UiPanel
from PyQt5.QtCore import Qt



class UiPanelConfig(UiPanel):
	# Initializes and displays a Panel

	FIXED_WIDTH = 400
		
	def __init__(self, title, panel, args):
		super().__init__(title)

		self.configs_fname = args['configs_fname']
		self.settingsCallback = args['settings_callback']

		with open(self.configs_fname, 'r') as fp:
			self.configs = json.load(fp)
		#print(self.configs)

		self.configSummaries = []
		for config in self.configs['configs']:
			self.configSummaries.append(config['summary'])

		self.panel			= panel
		self.widgetConfig		= self.addComboBox('Config', self.configSummaries)
		self.widgetConfig.setCurrentIndex(self.configs['selectedIndex'])

		self.widgetTelescope		= self.addLineEdit('Telescope', editable=False)
		self.widgetMount		= self.addLineEdit('Mount', editable=False)
		self.widgetFocalReducers	= self.addLineEdit('Focal Reducers', editable=False)
		self.widgetFocalLength		= self.addLineEditInt('Focal Length (mm)', 1, 10000)

		self.updateDisplayForConfigSelection(self.configs['selectedIndex'])

		self.widgetOK		= self.addButton('Start Astrid')
		self.widgetCancel	= self.addButton('Cancel')

		self.setColumnWidth(1, UiPanelConfig.FIXED_WIDTH)


	def registerCallbacks(self):
		self.widgetConfig.currentTextChanged.connect(self.comboBoxConfigChanged)
		self.widgetOK.clicked.connect(self.buttonOKPressed)
		self.widgetFocalLength.editingFinished.connect(self.focalLengthChanged)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def comboBoxConfigChanged(self, text):
		selectedIndex = self.configSummaries.index(text)
		self.updateDisplayForConfigSelection(selectedIndex)


	def focalLengthChanged(self):
		txt = self.widgetFocalLength.text()
		selectedIndex = self.widgetConfig.currentIndex()
		config = self.configs['configs'][selectedIndex]
		platesolver_fname = os.path.dirname(self.configs_fname) + '/' + config['configFolder'] + '/platesolver.json'
		with open(platesolver_fname, 'r') as fp:
			platesolver = json.load(fp)
		settings_focal_length = int(platesolver['focal_length'])
		entered_focal_length = int(txt)
		if entered_focal_length != settings_focal_length:
			platesolver['focal_length'] = float(entered_focal_length)
			jstr = json.dumps(platesolver, indent=4)
	
			with open(platesolver_fname, 'w') as fp:
				fp.write(jstr)
				fp.write('\n')

		astrometryCfg = os.path.dirname(self.configs_fname) + '/' + config['configFolder'] + '/astrometry.cfg'
		os.remove(astrometryCfg)
		

	def buttonOKPressed(self):
		selectedIndex = self.widgetConfig.currentIndex()

		# Tell main app that we're using the selected settings
		configBase = os.path.dirname(self.configs_fname)
		settings_folder = configBase + '/' + self.configs['configs'][selectedIndex]['configFolder']
		self.settingsCallback(settings_folder, self.configs['configs'][selectedIndex]['summary'])

		# Write the settings if selectedIndex has changed
		if selectedIndex != self.configs['selectedIndex']:
			self.configs['selectedIndex'] = selectedIndex
			jstr = json.dumps(self.configs, indent=4)

			with open(self.configs_fname, 'w') as fp:
				fp.write(jstr)

		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()


	# OPERATIONS

	def updateDisplayForConfigSelection(self, selectedIndex):
		config = self.configs['configs'][selectedIndex]
		self.widgetTelescope.setText(config['telescope'])
		self.widgetMount.setText(config['mount'])
		self.widgetFocalReducers.setText(config['focalreducers'])

		platesolver_fname = os.path.dirname(self.configs_fname) + '/' + config['configFolder'] + '/platesolver.json'
		with open(platesolver_fname, 'r') as fp:
			platesolver = json.load(fp)
		self.widgetFocalLength.setText(str(int(platesolver['focal_length'])))
