import os
import json
from UiPanel import UiPanel
from PyQt5.QtCore import Qt
from UiDialogPanel import UiDialogPanel
from UiPanelConfigSettings import UiPanelConfigSettings
from settings import Settings



class UiPanelConfig(UiPanel):
	# Initializes and displays a Panel

	FIXED_WIDTH = 400
		
	def __init__(self, title, panel, args):
		super().__init__(title)

		self.configs_fname = args['configs_fname']
		self.astrid_drive = args['astrid_drive']
		self.settingsCallback = args['settings_callback']
		self.stylesheetCallback = args['stylesheet_callback']

		with open(self.configs_fname, 'r') as fp:
			self.configs = json.load(fp)
		#print(self.configs)

		self.configSummaries = []
		for config in self.configs['configs']:
			self.configSummaries.append(config['summary'])

		self.panel			= panel
		self.widgetConfig		= self.addComboBox('Config', self.configSummaries)
		self.widgetConfig.setObjectName('comboBoxConfigSummary')
		self.widgetConfig.setCurrentIndex(self.configs['selectedIndex'])

		self.widgetTelescope		= self.addLineEdit('Telescope', editable=False)
		self.widgetMount		= self.addLineEdit('Mount', editable=False)
		self.widgetFocalReducers	= self.addLineEdit('Focal Reducers', editable=False)

		self.updateDisplayForConfigSelection(self.configs['selectedIndex'])

		tmp = os.listdir('stylesheets')
		self.colorSchemes = []
		for t in tmp:
			if t.endswith('.colorscheme'):
				self.colorSchemes.append(t.replace('.colorscheme', ''))

		self.widgetColorScheme		= self.addComboBox('Color Scheme', self.colorSchemes)
		self.widgetColorScheme.setObjectName('comboBoxConfigColorScheme')
		self.widgetColorScheme.setCurrentIndex(self.colorSchemes.index(self.configs['selectedColorScheme']))

		self.widgetOK			= self.addButton('Start Astrid')
		self.widgetSettings		= self.addButton('Settings')
		self.widgetCancel		= self.addButton('Cancel')

		self.setColumnWidth(1, UiPanelConfig.FIXED_WIDTH)


	def registerCallbacks(self):
		self.widgetConfig.currentTextChanged.connect(self.comboBoxConfigChanged)
		self.widgetSettings.clicked.connect(self.buttonSettingsPressed)
		self.widgetColorScheme.currentTextChanged.connect(self.comboBoxColorSchemeChanged)
		self.widgetOK.clicked.connect(self.buttonOKPressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def comboBoxConfigChanged(self, text):
		selectedIndex = self.configSummaries.index(text)
		self.updateDisplayForConfigSelection(selectedIndex)


	def comboBoxColorSchemeChanged(self, text):
		self.configs['selectedColorScheme'] = text
		self.__writeConfigs()
		self.stylesheetCallback()


	def buttonSettingsPressed(self):
		self.settingsDialog = UiDialogPanel('Config Settings', UiPanelConfigSettings, args = {'configs_fname': self.configs_fname, 'config_changed_callback': self.configChanged, 'selectedIndex': self.widgetConfig.currentIndex()})


	def buttonOKPressed(self):
		selectedIndex = self.widgetConfig.currentIndex()

		# Tell main app that we're using the selected settings
		configBase = os.path.dirname(self.configs_fname)
		settings_folder = configBase + '/' + self.configs['configs'][selectedIndex]['configFolder']

		# Write the settings if selectedIndex has changed
		if selectedIndex != self.configs['selectedIndex']:
			self.configs['selectedIndex'] = selectedIndex
			self.__writeConfigs()

		self.settingsCallback(settings_folder, self.configs['configs'][selectedIndex]['summary'])

		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()


	# OPERATIONS

	def updateDisplayForConfigSelection(self, selectedIndex):
		config = self.configs['configs'][selectedIndex]
		self.widgetTelescope.setText(config['telescope'])
		self.widgetMount.setText(config['mount'])
		self.widgetFocalReducers.setText(config['focalreducers'])

		# Read the settings
		selectedIndex = self.widgetConfig.currentIndex()
		configBase = os.path.dirname(self.configs_fname)
		settings_folder = configBase + '/' + self.configs['configs'][selectedIndex]['configFolder']
		Settings(settings_folder, self.astrid_drive, self.astrid_drive + '/configs')


	def configChanged(self):
		self.settingsCallback(None, None)

	
	def __writeConfigs(self):
		jstr = json.dumps(self.configs, indent=4)

		with open(self.configs_fname, 'w') as fp:
			fp.write(jstr)
