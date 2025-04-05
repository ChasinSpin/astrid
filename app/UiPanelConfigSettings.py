from processlogger import ProcessLogger
import os
import re
import copy
import json
import shutil
from UiPanel import UiPanel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from settings import Settings



class UiPanelConfigSettings(UiPanel):
	# Initializes and displays a Panel

	FIXED_WIDTH = 700
	FIELD_VALUE_FIXED_WIDTH = 300
	FIXED_WIDTH_TEXT_INFO = FIXED_WIDTH - 40


	def __init__(self, title, panel, args):
		super().__init__(title)

		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()

		self.configs_fname = args['configs_fname']
		self.configChangedCallback = args['config_changed_callback']
		self.selectedIndex = args['selectedIndex']
		
		self.settingsChanged	= []
		self.configChanged	= False

		with open(self.configs_fname, 'r') as fp:
			self.configs = json.load(fp)
		#print(self.configs)

		self.config = self.configs['configs'][self.selectedIndex]

		self.folderChange = None

		self.panel = panel

		# Create tabs
		tabsTitles = []
		self.settingsPanels = []

		# Create the config panel
		tabsTitles.append('Config')
		sPanel = UiPanel('Config Details')
		sPanel.name = 'config'
		sPanel.widgets = []
		self.settingsPanels.append(sPanel)
		self.__createConfigDetailsPanel(sPanel)

		# Create the settings panels
		for s in Settings.subsettings:
			if s['editable']:
				tabsTitles.append(s['displayName'])
				sPanel = UiPanel(s['displayName'] + ' Settings')
				sPanel.name = s['name']
				sPanel.settings = s
				sPanel.widgetSettings = []
				self.settingsPanels.append(sPanel)
		self.widgetTabs	= self.addTabs(tabsTitles, self.settingsPanels)
		self.widgetTabs.setFixedWidth(UiPanelConfigSettings.FIXED_WIDTH)

		self.__addSettingsForSettingsPanels()

		self.widgetSave			= self.addButton('Save Changes')
		self.widgetCancel		= self.addButton('Cancel')

		self.setColumnWidth(1, UiPanelConfigSettings.FIXED_WIDTH)


	def registerCallbacks(self):
		self.widgetSave.clicked.connect(self.buttonSavePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def buttonSavePressed(self):
		if len(self.settingsChanged) > 0:
			self.logger.info('saving settings changes:')
			for s in self.settingsChanged:
				Settings.getInstance().writeSubsetting(s)
			self.settingsChanged = []
		else:
			self.logger.info('settings, there were no changes to save')
			 
		if self.configChanged:
			self.logger.info('saving config changes...')
			
			if self.folderChange is not None:
				self.__renameConfigFolder(self.folderChange[0], self.folderChange[1])
			jstr = json.dumps(self.configs, indent=4)

			with open(self.configs_fname, 'w') as fp:
				fp.write(jstr)

			self.configChangedCallback()

		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.logger.info('settings changed cancelled')
		Settings.getInstance().read()
		self.panel.cancelDialog()


	def buttonDuplicatePressed(self):
		self.config = self.configs['configs'][self.selectedIndex]

		self.newConfig			= copy.deepcopy(self.config)
		self.newConfig['summary']	+= 'Copy'
		self.newConfig['configFolder']	+= 'copy'

		self.logger.info('duplicating config %s to %s' % (self.config['summary'], self.newConfig['summary']))
		
		configBase = os.path.dirname(self.configs_fname)
		shutil.copytree(configBase + '/' + self.config['configFolder'], configBase + '/' + self.newConfig['configFolder'])

		self.config = self.configs['configs'].append(self.newConfig)
		
		self.selectedIndex = len(self.configs['configs']) - 1
		self.configs['selectedIndex'] = self.selectedIndex

		jstr = json.dumps(self.configs, indent=4)

		with open(self.configs_fname, 'w') as fp:
			fp.write(jstr)

		self.configChangedCallback()


	def buttonDeletePressed(self):
		if len(self.configs['configs']) > 1:
			ret = QMessageBox.question(self, ' ', 'Deleting this config and settings are permanent!\n\nAre you sure you wish to DELETE?', QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.Yes:
				self.logger.info('deleting config %s' % self.configs['configs'][self.selectedIndex]['summary'])

				configBase = os.path.dirname(self.configs_fname)
				configFolder = configBase + '/' + self.configs['configs'][self.selectedIndex]['configFolder']
				shutil.rmtree(configFolder)
			
				self.configs['configs'].pop(self.selectedIndex)
				self.selectedIndex -= 1
				if self.selectedIndex < 0:
					self.selectedIndex = 1

				self.configs['selectedIndex'] = self.selectedIndex
	
				jstr = json.dumps(self.configs, indent=4)

				with open(self.configs_fname, 'w') as fp:
					fp.write(jstr)

				self.configChangedCallback()


	def boolChanged(self, state, panel, widget):
		oldValue = getattr(Settings.getInstance(), panel.name)[widget.name]
		newValue = widget.checkState() 
		if newValue == 2:
			newValue = True
		else:
			newValue = False	
		self.logger.info('setting changed (not saved yet): panel=%s setting=%s oldValue=%s newValue=%s' %  (panel.name, widget.name, str(oldValue), str(newValue)))
		if newValue != oldValue:
			getattr(Settings.getInstance(), panel.name)[widget.name] = newValue
			if not panel.name in self.settingsChanged:
				self.settingsChanged.append(panel.name)


	def intChanged(self, panel, widget):
		oldValue = getattr(Settings.getInstance(), panel.name)[widget.name]
		newValue = widget.text() 
		self.logger.info('setting changed (not saved yet): panel=%s setting=%s oldValue=%s newValue=%s' %  (panel.name, widget.name, oldValue, newValue))
		newValue = int(newValue)
		if newValue != oldValue:
			getattr(Settings.getInstance(), panel.name)[widget.name] = newValue
			if not panel.name in self.settingsChanged:
				self.settingsChanged.append(panel.name)


	def floatChanged(self, panel, widget):
		oldValue = getattr(Settings.getInstance(), panel.name)[widget.name]
		newValue = widget.text() 
		self.logger.info('setting changed (not saved yet): panel=%s setting=%s oldValue=%s newValue=%s' %  (panel.name, widget.name, oldValue, newValue))
		newValue = float(newValue)
		if newValue != oldValue:
			getattr(Settings.getInstance(), panel.name)[widget.name] = newValue
			if not panel.name in self.settingsChanged:
				self.settingsChanged.append(panel.name)
	

	def strChanged(self, panel, widget):
		oldValue = getattr(Settings.getInstance(), panel.name)[widget.name]
		newValue = widget.text() 
		self.logger.info('setting changed (not saved yet): panel=%s setting=%s oldValue=%s newValue=%s' %  (panel.name, widget.name, oldValue, newValue))
		if newValue != oldValue:
			getattr(Settings.getInstance(), panel.name)[widget.name] = newValue
			if not panel.name in self.settingsChanged:
				self.settingsChanged.append(panel.name)


	def choiceChanged(self, text, panel, widget):
		oldValue = getattr(Settings.getInstance(), panel.name)[widget.name]
		newValue = widget.currentText() 
		self.logger.info('setting changed (not saved yet): panel=%s setting=%s oldValue=%s newValue=%s' %  (panel.name, widget.name, oldValue, newValue))
		if newValue != oldValue:
			getattr(Settings.getInstance(), panel.name)[widget.name] = newValue
			if not panel.name in self.settingsChanged:
				self.settingsChanged.append(panel.name)


	def configStrChanged(self, widget):
		oldValue = self.configs['configs'][self.selectedIndex][widget.name]
		newValue = widget.text() 
		self.logger.info('config setting changed (not saved yet): setting=%s oldValue=%s newValue=%s' %  (widget.name, oldValue, newValue))
		if newValue != oldValue:
			if widget.name == 'configFolder':
				pattern = re.compile('[A-Za-z0-9\_\.]+')
				if pattern.fullmatch(newValue):
					configBase = os.path.dirname(self.configs_fname)
					if self.folderChange is None:
						self.folderChange = (configBase + '/' + oldValue, configBase + '/' + newValue)
					else:
						self.folderChange = (self.folderChange[0], configBase + '/' + newValue)

					self.configChanged = True
				else:
					widget.setText(oldValue)
					QMessageBox.warning(self, ' ', 'Config Folders can only contain characters [A-Z][a-z][0-9]_.', QMessageBox.Ok)
			else:
				self.configs['configs'][self.selectedIndex][widget.name] = newValue
				self.configChanged = True


	# OPERATIONS

	def __renameConfigFolder(self, oldFolder, newFolder):
		os.rename(oldFolder, newFolder)
		self.configs['configs'][self.selectedIndex]['configFolder'] = os.path.basename(newFolder)


	def __addFields(self, user_setting, panel):
		group_name = user_setting['group']
		current_settings = getattr(Settings.getInstance(), group_name)

		for s in user_setting['settings']:
			if   s['type'] == 'bool':
				widget = panel.addCheckBox(s['displayName'])
				widget.name = s['name']
				widget.setChecked(current_settings[s['name']])
				widget.stateChanged.connect(lambda state, w=widget, p=panel: self.boolChanged(state, p, w))

			elif s['type'] == 'int':
				widget = panel.addLineEditInt(s['displayName'], s['range'][0], s['range'][1])
				widget.name = s['name']
				widget.setText(str(current_settings[s['name']]))
				widget.editingFinished.connect(lambda w=widget, p=panel: self.intChanged(p, w))

			elif s['type'] == 'float':
				widget = panel.addLineEditDouble(s['displayName'], s['range'][0], s['range'][1], s['decimalPlaces'])
				widget.name = s['name']
				widget.setText(str(current_settings[s['name']]))
				widget.editingFinished.connect(lambda w=widget, p=panel: self.floatChanged(p, w))

			elif s['type'] == 'str':
				widget = panel.addLineEdit(s['displayName'])
				widget.name = s['name']
				widget.setText(current_settings[s['name']])
				widget.editingFinished.connect(lambda w=widget, p=panel: self.strChanged(p, w))

			elif s['type'] == 'choice':
				widget = panel.addComboBox(s['displayName'], s['range'])
				widget.setObjectName('comboBoxConfigSetting')
				widget.name = s['name']
				widget.setCurrentText(current_settings[s['name']])
				widget.currentTextChanged.connect(lambda text, w=widget, p=panel: self.choiceChanged(text, p, w))

			else:
				raise ValueError('Unrecognized settings type: %s' % s['type'])

			widget.setEnabled(s['editable'])
			widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
			panel.widgetSettings.append(widget)

		widget = panel.addTextBox('See: github.com/ChasinSpin/astrid/blob/main/docs/Configuration.md', height = 32)
		widget.setFixedWidth(UiPanelConfigSettings.FIXED_WIDTH_TEXT_INFO)


	def __addSettingsForSettingsPanels(self):
		for panel in self.settingsPanels:
			# Find the user_setting
			user_setting = None
			for user_setting in Settings.user_settings:		
				if user_setting['group'] == panel.name and panel.settings['editable']:
					self.__addFields(user_setting, panel)


	def __createConfigDetailsPanel(self, sPanel):
		widget = sPanel.addTextBox('Note: Any changes to the these settings will require a restart of the application.', height = 60)
		widget.setFixedWidth(UiPanelConfigSettings.FIXED_WIDTH_TEXT_INFO)

		widget = sPanel.addLineEdit('Config Name')
		widget.name = 'summary'
		widget.setText(self.config['summary'])
		widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
		widget.editingFinished.connect(lambda w=widget: self.configStrChanged(w))
		sPanel.widgets.append(widget)

		widget = sPanel.addLineEdit('Config Folder')
		widget.name = 'configFolder'
		widget.setText(self.config['configFolder'])
		widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
		widget.editingFinished.connect(lambda w=widget: self.configStrChanged(w))
		sPanel.widgets.append(widget)

		widget = sPanel.addLineEdit('Mount')
		widget.name = 'mount'
		widget.setText(self.config['mount'])
		widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
		widget.editingFinished.connect(lambda w=widget: self.configStrChanged(w))
		sPanel.widgets.append(widget)

		widget = sPanel.addLineEdit('Telescope')
		widget.name = 'telescope'
		widget.setText(self.config['telescope'])
		widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
		widget.editingFinished.connect(lambda w=widget: self.configStrChanged(w))
		sPanel.widgets.append(widget)

		widget = sPanel.addLineEdit('Focal Reducers')
		widget.name = 'focalreducers'
		widget.setText(self.config['focalreducers'])
		widget.setFixedWidth(UiPanelConfigSettings.FIELD_VALUE_FIXED_WIDTH)
		widget.editingFinished.connect(lambda w=widget: self.configStrChanged(w))
		sPanel.widgets.append(widget)

		self.widgetSpacer = sPanel.addSpacer()

		self.widgetDuplicateConfig = sPanel.addButton('Duplicate This Config')
		self.widgetDuplicateConfig.clicked.connect(self.buttonDuplicatePressed)

		self.widgetDeleteConfig = sPanel.addButton('Delete This Config')
		self.widgetDeleteConfig.clicked.connect(self.buttonDeletePressed)
