import os
import json
from pprint import *


# Tuple:
#	'camera' etc. = Json file and name of setting
#	true = json is within the setting subdirectory
#	false = json is within the config folder (not a subdirectory)
subsettings = [('camera', True), ('mount', True), ('objects', False), ('platesolver', True), ('occultations', False), ('site', True), ('observer', False)]


master_settings = [
	# configs.json
	# objects.json
	# observer.json
	# occultations.json

	# camera.json
	# mount.json
	# platesolver.json
	# site.json

	# Notes:
	# hflip/vflip changed from 0/1 to False/True
	# "dither": {
	#	"ra": 0.001,
	#	"dec": 0.01
	# },
	# changed to:
	# dither_ra and dither_decd
	{'group': 'camera', 'settings': [
		{'name': 'mode_selected',			'type': 'int',		'range': [1, 1],			'default': 1},
		{'name': 'hflip',				'type': 'bool',		'range': None,				'default': False},
		{'name': 'vflip',				'type': 'bool',		'range': None,				'default': False},
		{'name': 'gain',				'type': 'float',	'range': [1.0, 16.0],			'default': 4.0},
		{'name': 'accelerted_preview',			'type': 'bool',		'range': None,				'default': False},
		{'name': 'photo_format',			'type': 'choice',	'range': ['fit'],			'default': 'fit'},
		{'name': 'radec_format',			'type': 'choice',	'range': ['hmsdms','hour','deg'],	'default': 'hmsdms'},
		{'name': 'polar_align_test',			'type': 'bool',		'range': None,				'default': False},
		{'name': 'polar_align_rotation',		'type': 'float',	'range': [60.0,90.0],			'default': 90.0},
		{'name': 'default_photo_exposure',		'type': 'float',	'range': [0.01,30.0],			'default': 1.0},
		{'name': 'prompt_dark_after_acquisition',	'type': 'bool',		'range': None,				'default': True},
		{'name': 'dither_ra',				'type': 'float',	'range': [0.00001,1.0],			'default': 0.001},
		{'name': 'dither_dec',				'type': 'float',	'range': [0.0001,10.0],			'default': 0.01},
		{'name': 'photosFolder',			'type': 'str',		'range': None,				'default': '/media/pi/ASTRID/Photo'},
		{'name': 'videoFolder',				'type': 'str',		'range': None,				'default': '/media/pi/ASTRID/OTEVideo'},
	]},

	{'group': 'mount', 'settings': [
		{'name': 'name',				'type': 'str',		'range': None,				'default': 'Simulator'},
		{'name': 'indi_module',				'type': 'str',		'range': None,				'default': 'indi_simulator_telescope'},
		{'name': 'indi_telescope_device_id',		'type': 'str',		'range': None,				'default': 'Telescope Simulator'},
		{'name': 'indi_usb_tty',			'type': 'str',		'range': None,				'default': '/dev/ttyUSB0'},
		{'name': 'baud',				'type': 'int',		'range': [1200,256000],			'default': 9600},
		{'name': 'align_axis',				'type': 'choice',	'range': ['eq','altaz'],		'default': 'eq'},
		{'name': 'goto_capable',			'type': 'bool',		'range': None,				'default': True},
		{'name': 'tracking_capable',			'type': 'bool',		'range': None,				'default': True},
		{'name': 'mount_is_j2000',			'type': 'bool',		'range': None,				'default': False},
		{'name': 'local_offset',			'type': 'float',	'range': [0.0,0.0],			'default': 0.0},
		{'name': 'parkmethod',				'type': 'choice',	'range': ['park','home'],		'default': 'home'},
		{'name': 'debug',				'type': 'bool',		'range': None,				'default': False},
	]},

	{'group': 'platesolver', 'settings': [
	]},
	{'group': 'site', 'settings': [
	]},

	{'group': 'objects', 'settings': [
	]},
	{'group': 'observer', 'settings': [
	]},
	{'group': 'occultations', 'settings': [
	]},
]


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
