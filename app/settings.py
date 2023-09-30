from processlogger import ProcessLogger
import os
import json
import copy
from pprint import *


# name= The Json filename name of the setting
# global=
#	True = json is within the setting subdirectory
#	False = json is within the config folder (not a subdirectory)
subsettings = [
	{'name': 'camera',		'global': True,		'editable': True,	'displayName': 'Camera'},
	{'name': 'mount',		'global': True,		'editable': True,	'displayName': 'Mount'},
	{'name': 'objects',		'global': False,	'editable': False,	'displayName': 'Objects'},
	{'name': 'platesolver',		'global': True,		'editable': True,	'displayName': 'Plate Solver'},
	{'name': 'occultations',	'global': False,	'editable': False,	'displayName': 'Occultations'},
	{'name': 'site',		'global': True,		'editable': False,	'displayName': 'Site'},
	{'name': 'observer',		'global': False,	'editable': True,	'displayName': 'Observer'}
]


# User Settings
#	Anything not on this list is deleted
#	Anything on this list but not in the json is created
user_settings = [
	{'group': 'camera', 'settings': [
		{'name': 'mode_selected',			'type': 'int',		'range': [1, 1],				'default': 1,				'editable': True,	'displayName': 'Mode Selected',				'description': ''},
		{'name': 'hflip',				'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Horizontal Flip',			'description': ''},
		{'name': 'vflip',				'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Vertical Flip',				'description': ''},
		{'name': 'gain',				'type': 'float',	'range': [1.0, 16.0],				'default': 4.0,				'editable': True,	'displayName': 'Gain',					'description': ''},
		{'name': 'accelerated_preview',			'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Accelerated Preview',			'description': ''},
		{'name': 'photo_format',			'type': 'choice',	'range': ['fit'],				'default': 'fit',			'editable': False,	'displayName': 'Photo Format',				'description': ''},
		{'name': 'radec_format',			'type': 'choice',	'range': ['hmsdms','hour','deg'],		'default': 'hmsdms',			'editable': True,	'displayName': 'Ra/Dec Display Format',			'description': ''},
		{'name': 'polar_align_test',			'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Polar Align Test Mode',			'description': ''},
		{'name': 'polar_align_rotation',		'type': 'float',	'range': [60.0,90.0],				'default': 90.0,			'editable': True,	'displayName': 'Polar Align Rotation amount',		'description': ''},
		{'name': 'default_photo_exposure',		'type': 'float',	'range': [0.01,30.0],				'default': 1.0,				'editable': True,	'displayName': 'Default Photo Exposure',		'description': ''},
		{'name': 'prompt_dark_after_acquisition',	'type': 'bool',		'range': None,					'default': True,			'editable': True,	'displayName': 'Prompt For Darks After Acquisition',	'description': ''},
		{'name': 'dither_ra',				'type': 'float',	'range': [0.00001,1.0],				'default': 0.001,			'editable': True,	'displayName': 'Dithering RA Amount',			'description': ''},
		{'name': 'dither_dec',				'type': 'float',	'range': [0.0001,10.0],				'default': 0.01,			'editable': True,	'displayName': 'Dithering DEC Amount',			'description': ''},
		{'name': 'photosFolder',			'type': 'str',		'range': None,					'default': '/media/pi/ASTRID/Photo',	'editable': False,	'displayName': 'Photos Folder Location',		'description': ''},
		{'name': 'videoFolder',				'type': 'str',		'range': None,					'default': '/media/pi/ASTRID/OTEVideo',	'editable': False,	'displayName': 'Video Folder Location',			'description': ''},
		{'name': 'buzzer_enable',			'type': 'bool',		'range': None,					'default': True,			'editable': True,	'displayName': 'Buzzer',				'description': ''},
	]},

	{'group': 'mount', 'settings': [
		{'name': 'name',				'type': 'str',		'range': None,					'default': 'Simulator',			'editable': True,	'displayName': 'Display Name',				'description': ''},
		{'name': 'indi_module',				'type': 'str',		'range': None,					'default': 'indi_simulator_telescope',	'editable': True,	'displayName': 'Indi Module',				'description': ''},
		{'name': 'indi_telescope_device_id',		'type': 'str',		'range': None,					'default': 'Telescope Simulator',	'editable': True,	'displayName': 'Indi Telescope Device Id',		'description': ''},
		{'name': 'indi_usb_tty',			'type': 'str',		'range': None,					'default': '/dev/ttyUSB0',		'editable': True,	'displayName': 'Indi USB tty',				'description': ''},
		{'name': 'baud',				'type': 'int',		'range': [1200,256000],				'default': 9600,			'editable': True,	'displayName': 'Baud Rate',				'description': ''},
		{'name': 'align_axis',				'type': 'choice',	'range': ['eq','altaz'],			'default': 'eq',			'editable': True,	'displayName': 'Mount Alignment Type',			'description': ''},
		{'name': 'goto_capable',			'type': 'bool',		'range': None,					'default': True,			'editable': True,	'displayName': 'Goto Capability',			'description': ''},
		{'name': 'tracking_capable',			'type': 'bool',		'range': None,					'default': True,			'editable': True,	'displayName': 'Tracking Capability',			'description': ''},
		{'name': 'mount_is_j2000',			'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Mount is J2000',			'description': ''},
		{'name': 'local_offset',			'type': 'float',	'range': [-24.0,24.0],				'default': 0.0,				'editable': False,	'displayName': 'Local Timezone Offset',			'description': ''},
		{'name': 'parkmethod',				'type': 'choice',	'range': ['park','home'],			'default': 'home',			'editable': True,	'displayName': 'Parking Method',			'description': ''},
		{'name': 'debug',				'type': 'bool',		'range': None,					'default': False,			'editable': True,	'displayName': 'Indi Debug',				'description': ''},
	]},

	{'group': 'platesolver', 'settings': [
		{'name': 'focal_length',			'type': 'float',	'range': [2, 5000],				'default': 200.0,			'editable': False,	'displayName': 'Focal Length',				'description': ''},
		{'name': 'search_radius_deg',			'type': 'float',	'range': [0.1, 30.0],				'default': 5.0,				'editable': True,	'displayName': 'Search Radius(deg)',			'description': ''},
		{'name': 'limit_objs',				'type': 'int',		'range': [10, 10000],				'default': 1002,			'editable': True,	'displayName': 'Limit Results Objects',			'description': ''},
		{'name': 'downsample',				'type': 'int',		'range': [1, 10],				'default': 2,				'editable': True,	'displayName': 'Downsample Image',			'description': ''},
		{'name': 'source_extractor',			'type': 'bool',		'range': None,					'default': True,			'editable': True,	'displayName': 'Use Source Extractor',			'description': ''},
		{'name': 'scale_low_factor',			'type': 'float',	'range': [0.01, 10.0],				'default': 0.1,				'editable': True,	'displayName': 'Focal Length Low Factor',		'description': ''},
		{'name': 'scale_high_factor',			'type': 'float',	'range': [0.01, 10.0],				'default': 1.25,			'editable': True,	'displayName': 'Focal Length High Factor',		'description': ''},
		{'name': 'direction_indicator_polar_align',	'type': 'choice',	'range': ['None', '1 Arrow', '2 Arrows'],	'default': 2,				'editable': True,	'displayName': 'Direction Indicator for Polar Align',	'description': ''},
		{'name': 'direction_indicator_platesolve',	'type': 'choice',	'range': ['None', '1 Arrow', '2 Arrows'],	'default': 1,				'editable': True,	'displayName': 'Direction Indicator for Plate Solving',	'description': ''},
	]},

	{'group': 'observer', 'settings': [
		{'name': 'observer_name',			'type': 'str',		'range': None,					'default': 'John Doe',			'editable': True,	'displayName': 'Observer Name',				'description': ''},
		{'name': 'observer_id',				'type': 'str',		'range': None,					'default': 'johndoe@johndoe.com',	'editable': True,	'displayName': 'Observer Indentifier',			'description': ''},
	]},
]



# Singleton

class Settings:

	__instance = None
	settings_folder = None
	configs_folder = None

	def __init__(self, settings_folder, astrid_drive, configs_folder):
		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()

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
		if subsetting['global']:
			settings_fname = Settings.settings_folder + '/' + subsetting['name'] + '.json'
		else:
			settings_fname = Settings.configs_folder + '/' + subsetting['name'] + '.json'
		return settings_fname


	def __updateSettings(self, setting_name, setting_sub):
		setting_dict = getattr(self, setting_name)

		# Obtain the correct subsetting information
		for subsetting in subsettings:
			if subsetting['name'] == setting_name:
				break

		# Find the group
		group_settings = None
		for usetting in user_settings:
			if usetting['group'] == setting_name:
				group_settings = usetting
				break

		# Validate the settings
		settings_changed = False
		if group_settings is not None:
			# Roll through the settings in the json and delete the ones we shouldn't have
			setting_keys = copy.deepcopy(setting_dict).keys()
			for s in setting_keys:
				found = False
				for g in group_settings['settings']:
					if g['name'] == s:
						found = True
						break

				if not found:
					self.logger.info('settings DELETE %s from %s.json' % (s, setting_name))
					del setting_dict[s]
					settings_changed = True

			# Roll through the settings we should have, and create those that don't exist
			for s in group_settings['settings']:
				if not s['name'] in setting_dict:
					self.logger.info('settings CREATE %s in %s.json' % (s['name'], setting_name))
					setting_dict[s['name']] = s['default']
					settings_changed = True

			# Roll through the settings looking for:
			# 	bool that is 0 or 1 and change to True or False
			# 	choice that is a number and set to the string
			for s in group_settings['settings']:
				sname = s['name']

				#self.logger.info('settings type: %s setting_dict[sname]: %s typeof: %s' % (s['type'], setting_dict[sname], type(setting_dict[sname])))

				if s['type'] == 'bool' and type(setting_dict[sname]) is int:
					self.logger.info('settings UPDATED %s in %s.json to True/False' % (sname, setting_name))
					setting_dict[sname] = True if setting_dict[sname] == 1 else False
					settings_changed = True
			
				if s['type'] == 'choice' and type(setting_dict[sname]) is int:
					self.logger.info('settings UPDATED %s in %s.json to choices string' % (sname, setting_name))
					setting_dict[sname] = s['range'][setting_dict[sname]]
					settings_changed = True

		if settings_changed:
			self.writeSubsetting(setting_name)


	def read(self):
		for subsetting in subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			self.logger.info('reading settings: %s' % settings_fname)

			if os.path.isfile(settings_fname):
				with open(settings_fname, 'r') as fp:
					setattr(self, subsetting['name'], json.load(fp))
			else:
				setattr(self, subsetting['name'], {})

			self.__updateSettings(subsetting['name'], subsetting)


	def write(self):
		for subsetting in subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			self.info('Writing settings: %s' % settings_fname)

			with open(settings_fname, 'w') as fp:
				json.dump(getattr(self, subsetting['name']), fp)


	def writeSubsetting(self, subsetting):
		settings_fname = None
		for s in subsettings:
			if s['name'] == subsetting:
				settings_fname = self.__getSettingsFname(s)
		if settings_fname is None:
			raise ValueError('no subsetting %s found' % subsetting)

		self.logger.info('Writing settings: %s' % settings_fname)

		jstr = json.dumps(getattr(self, subsetting), indent=4)
		
		with open(settings_fname, 'w') as fp:
			fp.write(jstr)
			fp.write('\n')
