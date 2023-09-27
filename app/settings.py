import os
import json
from pprint import *


# Tuple:
#	'camera' etc. = Json file and name of setting
#	true = json is within the setting subdirectory
#	false = json is within the config folder (not a subdirectory)
subsettings = [('camera', True), ('mount', True), ('objects', False), ('platesolver', True), ('occultations', False), ('site', True), ('observer', False)]


# Singleton

class Settings:

	__instance = None
	settings_folder = None
	configs_folder = None

	def __init__(self, settings_folder, astrid_drive, configs_folder):
		Settings.settings_folder = settings_folder
		Settings.configs_folder = configs_folder
		if Settings.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			Settings.__instance = self
			self.read()
		self.astrid_drive = astrid_drive


	@staticmethod
	def getInstance():
		if Settings.__instance == None:
			Settings()
		return Settings.__instance


	def __getSettingsFname(self, subsetting):
		if subsetting[1]:
			settings_fname = Settings.settings_folder + '/' + subsetting[0] + '.json'
		else:
			settings_fname = Settings.configs_folder + '/' + subsetting[0] + '.json'
		return settings_fname


	def read(self):
		for subsetting in subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			print('Reading settings:', settings_fname)

			if os.path.isfile(settings_fname):
				with open(settings_fname, 'r') as fp:
					setattr(self, subsetting[0], json.load(fp))
			else:
				setattr(self, subsetting[0], {})


	def write(self):
		for subsetting in subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			print('Writing settings:', settings_fname)

			with open(settings_fname, 'w') as fp:
				json.dump(getattr(self, subsetting[0]), fp)


	def writeSubsetting(self, subsetting):
		settings_fname = None
		for s in subsettings:
			if s[0] == subsetting:
				settings_fname = self.__getSettingsFname(s)
		if settings_fname is None:
			raise ValueError('no subsetting %s found' % subsetting)

		print('Writing settings:', settings_fname)

		jstr = json.dumps(getattr(self, subsetting), indent=4)
		
		with open(settings_fname, 'w') as fp:
			fp.write(jstr)
			fp.write('\n')
