import logging
from processlogger import ProcessLogger
import os
import json
import copy
from pprint import *
from PyQt5.QtWidgets import QMessageBox



# Semi-Singleton
# Calling Settings(...) again recreates the singleton

class Settings:

	__instance = None
	settings_folder = None
	configs_folder = None

	# name= The Json filename name of the setting
	# global=
	#	True = json is within the setting subdirectory
	#	False = json is within the config folder (not a subdirectory)
	subsettings = [
		{'name': 'camera',		'global': True,		'editable': True,	'displayName': 'Camera'},
		{'name': 'mount',		'global': True,		'editable': True,	'displayName': 'Mount'},
		{'name': 'focus',		'global': True,		'editable': True,	'displayName': 'Focus'},
		{'name': 'objects',		'global': False,	'editable': False,	'displayName': 'Objects'},
		{'name': 'platesolver',		'global': True,		'editable': True,	'displayName': 'Plate Solver'},
		{'name': 'occultations',	'global': False,	'editable': False,	'displayName': 'Occultations'},
		{'name': 'site',		'global': True,		'editable': False,	'displayName': 'Site'},
		{'name': 'observer',		'global': False,	'editable': True,	'displayName': 'Observer'},
		{'name': 'telescope',		'global': True,		'editable': True,	'displayName': 'Telescope'},
		{'name': 'general',		'global': True,		'editable': True,	'displayName': 'General'},
		{'name': 'hidden',		'global': False,	'editable': False,	'displayName': 'Hidden'},
	]


	# User Settings
	#	Anything not on this list is deleted
	#	Anything on this list but not in the json is created
	user_settings = [
		{'group': 'camera', 'settings': [
			{'name': 'mode_selected',			'type': 'int',		'range': [1, 1],				'default': 1,				'decimalPlaces': None,	'editable': False,	'displayName': 'Mode Selected',				'description': ''},
			{'name': 'hflip',				'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Horizontal Flip',			'description': ''},
			{'name': 'vflip',				'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Vertical Flip',				'description': ''},
			{'name': 'gain',				'type': 'float',	'range': [1.0, 16.0],				'default': 4.0,				'decimalPlaces': 1,	'editable': True,	'displayName': 'Gain',					'description': ''},
			{'name': 'accelerated_preview',			'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': False,	'displayName': 'Accelerated Preview',			'description': ''},
			{'name': 'photo_format',			'type': 'choice',	'range': ['fit'],				'default': 'fit',			'decimalPlaces': None,	'editable': False,	'displayName': 'Photo Format',				'description': ''},
			{'name': 'radec_format',			'type': 'choice',	'range': ['hmsdms','hour','deg'],		'default': 'hmsdms',			'decimalPlaces': None,	'editable': True,	'displayName': 'Ra/Dec Display Format',			'description': ''},
			{'name': 'polar_align_test',			'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Polar Align Test Mode',			'description': ''},
			{'name': 'polar_align_rotation',		'type': 'float',	'range': [60.0,90.0],				'default': 90.0,			'decimalPlaces': 1,	'editable': True,	'displayName': 'Polar Align Rotation amount',		'description': ''},
			{'name': 'default_photo_exposure',		'type': 'float',	'range': [0.0,30.0],				'default': 1.0,				'decimalPlaces': 6,	'editable': True,	'displayName': 'Default Photo Exposure',		'description': ''},
			{'name': 'prompt_dark_after_acquisition2',	'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Prompt For Darks After Acquisition',	'description': ''},
			{'name': 'dither_ra',				'type': 'float',	'range': [0.0,10.0],				'default': 0.001,			'decimalPlaces': 6,	'editable': True,	'displayName': 'Dithering RA Amount',			'description': ''},
			{'name': 'dither_dec',				'type': 'float',	'range': [0.0,10.0],				'default': 0.01,			'decimalPlaces': 6,	'editable': True,	'displayName': 'Dithering DEC Amount',			'description': ''},
			{'name': 'photosFolder',			'type': 'str',		'range': None,					'default': '/media/pi/ASTRID/Photo',	'decimalPlaces': None,	'editable': False,	'displayName': 'Photos Folder Location',		'description': ''},
			{'name': 'videoFolder',				'type': 'str',		'range': None,					'default': '/media/pi/ASTRID/OTEVideo',	'decimalPlaces': None,	'editable': False,	'displayName': 'Video Folder Location',			'description': ''},
			{'name': 'buzzer_enable',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Buzzer',				'description': ''},
		]},

		{'group': 'mount', 'settings': [
			{'name': 'name',				'type': 'str',		'range': None,					'default': 'Simulator',			'decimalPlaces': None,	'editable': True,	'displayName': 'Display Name',				'description': ''},
			{'name': 'indi_module',				'type': 'choice',	'range': ['indi_simulator_telescope', 'indi_astrotrac_telescope', 'indi_azgti_telescope', 'indi_bresserexos2', 'indi_celestron_aux', 'indi_celestron_gps', 'indi_crux_mount', 'indi_dsc_telescope', 'indi_eq500x_telescope', 'indi_eqmod_telescope', 'indi_ieqlegacy_telescope', 'indi_ieq_telescope', 'indi_ioptronHC8406', 'indi_ioptronv3_telescope', 'indi_lx200_10micron', 'indi_lx200_16', 'indi_lx200am5', 'indi_lx200aok', 'indi_lx200ap_v2', 'indi_lx200autostar', 'indi_lx200basic', 'indi_lx200classic', 'indi_lx200fs2', 'indi_lx200gemini', 'indi_lx200generic', 'indi_lx200gotonova', 'indi_lx200gps', 'indi_lx200_OnStep', 'indi_lx200_OpenAstroTech', 'indi_lx200_pegasus_nyx101', 'indi_lx200pulsar2', 'indi_lx200ss2000pc', 'indi_lx200stargo', 'indi_lx200_TeenAstro', 'indi_lx200zeq25', 'indi_paramount_telescope', 'indi_pmc8_telescope', 'indi_rainbow_telescope', 'indi_script_telescope', 'indi_skyadventurergti_telescope', 'indi_skycommander_telescope', 'indi_skywatcherAltAzMount', 'indi_staradventurer2i_telescope', 'indi_starbook_ten', 'indi_synscanlegacy_telescope', 'indi_synscan_telescope', 'indi_temma_telescope'],
																		'default': 'indi_simulator_telescope',	'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Module',				'description': ''},
			{'name': 'indi_telescope_device_id',		'type': 'str',		'range': None,					'default': 'Telescope Simulator',	'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Telescope Device Id',		'description': ''},
			{'name': 'indi_custom_properties',		'type': 'str',		'range': None,					'default': '',				'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Custom Properties',		'description': ''},
			{'name': 'indi_connection_method',		'type': 'choice',	'range': ['serial', 'ip address'],		'default': 'serial',			'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Connection Method',				'description': ''},
			{'name': 'baud',				'type': 'int',		'range': [110,256000],				'default': 9600,			'decimalPlaces': None,	'editable': True,	'displayName': 'Baud Rate',				'description': ''},
			{'name': 'ip_addr',				'type': 'str',		'range': None,					'default': '192.168.1.100',		'decimalPlaces': None,	'editable': True,	'displayName': 'IP Address',				'description': ''},
			{'name': 'ip_port',				'type': 'int',		'range': [1,65535],				'default': 10000,			'decimalPlaces': None,	'editable': True,	'displayName': 'IP Port',				'description': ''},
			{'name': 'align_axis',				'type': 'choice',	'range': ['eq','altaz'],			'default': 'eq',			'decimalPlaces': None,	'editable': True,	'displayName': 'Mount Alignment Type',			'description': ''},
			{'name': 'goto_capable',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Goto Capability',			'description': ''},
			{'name': 'tracking_capable',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Tracking Capability',			'description': ''},
			{'name': 'mount_is_j2000',			'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Mount is J2000',			'description': ''},
			{'name': 'set_time',				'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Set Time',			'description': ''},
			{'name': 'set_site',				'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Set Site',			'description': ''},
			{'name': 'local_offset',			'type': 'float',	'range': [-24.0,24.0],				'default': 0.0,				'decimalPlaces': 2,	'editable': False,	'displayName': 'Local Timezone Offset',			'description': ''},
			{'name': 'parkmethod',				'type': 'choice',	'range': ['park','home'],			'default': 'home',			'decimalPlaces': None,	'editable': True,	'displayName': 'Parking Method',			'description': ''},
			{'name': 'debug',				'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Debug',				'description': ''},
		]},

		{'group': 'focus', 'settings': [
			{'name': 'indi_module',				'type': 'choice',	'range': ['indi_aaf2_focus', 'indi_activefocuser_focus', 'indi_armadillo_focus', 'indi_asi_focuser', 'indi_celestron_sct_focus', 'indi_deepskydad_af1_focus', 'indi_deepskydad_af2_focus', 'indi_deepskydad_af3_focus', 'indi_dmfc_focus', 'indi_dreamfocuser_focus', 'indi_efa_focus', 'indi_esattoarco_focus', 'indi_esatto_focus', 'indi_fcusb_focus', 'indi_fli_focus', 'indi_gemini_focus', 'indi_hitecastrodc_focus', 'indi_integra_focus', 'indi_lacerta_mfoc_fmc_focus', 'indi_lacerta_mfoc_focus', 'indi_lakeside_focus', 'indi_lynx_focus', 'indi_microtouch_focus', 'indi_moonlitedro_focus', 'indi_moonlite_focus', 'indi_myfocuserpro2_focus', 'indi_nfocus', 'indi_nightcrawler_focus', 'indi_nstep_focus', 'indi_oasis_focuser', 'indi_onfocus_focus', 'indi_pegasus_focuscube', 'indi_perfectstar_focus', 'indi_platypus_focus', 'indi_rainbowrsf_focus', 'indi_rbfocus_focus', 'indi_robo_focus', 'indi_sestosenso2_focus', 'indi_sestosenso_focus', 'indi_siefs_focus', 'indi_simulator_focus', 'indi_smartfocus_focus', 'indi_steeldrive2_focus', 'indi_steeldrive_focus', 'indi_tcfs3_focus', 'indi_tcfs_focus', 'indi_teenastro_focus', 'indi_usbfocusv3_focus'],
																		'default': 'indi_simulator_focus',	'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Module',				'description': ''},
			{'name': 'indi_focuser_device_id',		'type': 'str',		'range': None,					'default': 'Focuser Simulator',		'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Focuser Device Id',		'description': ''},
			{'name': 'indi_custom_properties',		'type': 'str',		'range': None,					'default': '',				'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Custom Properties',		'description': ''},
			{'name': 'coarse_step',				'type': 'int',		'range': [0,65535],				'default': 50,				'decimalPlaces': None,	'editable': True,	'displayName': 'Coarse Step',				'description': ''},
			{'name': 'fine_step',				'type': 'int',		'range': [0,65535],				'default': 10,				'decimalPlaces': None,	'editable': True,	'displayName': 'Fine Step',				'description': ''},
			{'name': 'has_temperature',			'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Has Temperature Sensor',		'description': ''},
			{'name': 'debug',				'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Indi Debug',				'description': ''},
		]},
	
		{'group': 'platesolver', 'settings': [
			{'name': 'focal_length',			'type': 'float',	'range': [2, 5000],				'default': 200.0,			'decimalPlaces': 1,	'editable': True,	'displayName': 'Focal Length',				'description': ''},
			{'name': 'search_radius_deg',			'type': 'float',	'range': [1.0, 30.0],				'default': 5.0,				'decimalPlaces': 2,	'editable': True,	'displayName': 'Search Radius(deg)',			'description': ''},
			{'name': 'limit_objs',				'type': 'int',		'range': [5, 10000],				'default': 1002,			'decimalPlaces': None,	'editable': True,	'displayName': 'Limit Results Objects',			'description': ''},
			{'name': 'downsample',				'type': 'int',		'range': [1, 10],				'default': 2,				'decimalPlaces': None,	'editable': True,	'displayName': 'Downsample Image',			'description': ''},
			{'name': 'source_extractor',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Use Source Extractor',			'description': ''},
			{'name': 'scale_low_factor',			'type': 'float',	'range': [0.01, 0.9],				'default': 0.1,				'decimalPlaces': 2,	'editable': True,	'displayName': 'Focal Length Low Factor',		'description': ''},
			{'name': 'scale_high_factor',			'type': 'float',	'range': [1.01, 5.0],				'default': 1.25,			'decimalPlaces': 2,	'editable': True,	'displayName': 'Focal Length High Factor',		'description': ''},
			{'name': 'direction_indicator_polar_align',	'type': 'choice',	'range': ['None', '1 Arrow', '2 Arrows'],	'default': 2,				'decimalPlaces': None,	'editable': True,	'displayName': 'Direction Indicator for Polar Align',	'description': ''},
			{'name': 'direction_indicator_platesolve',	'type': 'choice',	'range': ['None', '1 Arrow', '2 Arrows', 'Ra/Dec'],
																		'default': 1,				'decimalPlaces': None,	'editable': True,	'displayName': 'Direction Indicator for Plate Solving',	'description': ''},
		]},
	
		{'group': 'observer', 'settings': [
			{'name': 'observer_name',			'type': 'str',		'range': None,					'default': 'John Doe',			'decimalPlaces': None,	'editable': True,	'displayName': 'Observer Full Name',			'description': ''},
			{'name': 'observer_id',				'type': 'str',		'range': None,					'default': 'johndoe@johndoe.com',	'decimalPlaces': None,	'editable': True,	'displayName': 'Observer Email',			'description': ''},
			{'name': 'owcloud_login',			'type': 'str',		'range': None,					'default': 'johndoe@johndoe.com',	'decimalPlaces': None,	'editable': True,	'displayName': 'OW Cloud Login',			'description': ''},
			{'name': 'owcloud_password',			'type': 'str',		'range': None,					'default': 'password',			'decimalPlaces': None,	'editable': True,	'displayName': 'OW Cloud Password',			'description': ''},
			{'name': 'owcloud_sitefilter',			'type': 'str',		'range': None,					'default': '',				'decimalPlaces': None,	'editable': True,	'displayName': 'OW Site Filter',			'description': ''},
			{'name': 'station_number',			'type': 'int',		'range': [1, 10000],				'default': 0,				'decimalPlaces': None,	'editable': True,	'displayName': 'Station Number',			'description': ''},
			{'name': 'create_na_report',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Create North American Report Form',	'description': ''},
		]},

		{'group': 'telescope', 'settings': [
			{'name': 'aperture',				'type': 'int',		'range': [5, 10000],				'default': 0,				'decimalPlaces': None,	'editable': True,	'displayName': 'Aperture(mm)',				'description': ''},
			{'name': 'optical_type',			'type': 'choice',	'range': ['SCT including Cass and Mak',
													  'Newtonian', 'Refractor',
													  'Dobsonian'],				'default': 'Refractor',			'decimalPlaces': None,	'editable': True,	'displayName': 'Optical Type',				'description': ''},
		]},

		{'group': 'general', 'settings': [
			{'name': 'fan_mode',				'type': 'choice',	'range': ['on', 'idle', 'off'],			'default': 0,				'decimalPlaces': None,	'editable': True,	'displayName': 'Fan Mode',				'description': ''},
			{'name': 'center_marker',			'type': 'choice',	'range': ['crosshairs', 'rectangle',
													  'small cross'],			'default': 2,				'decimalPlaces': None,	'editable': True,	'displayName': 'Center Marker Type',			'description': ''},
			{'name': 'voltage_warning',			'type': 'float',	'range': [0, 14],				'default': 11.5,			'decimalPlaces': 1,	'editable': True,	'displayName': 'Warning Voltage',			'description': ''},
			{'name': 'voltage_shutdown',			'type': 'float',	'range': [0, 12],				'default': 0,				'decimalPlaces': 1,	'editable': True,	'displayName': 'Shutdown Voltage',			'description': ''},
			{'name': 'location_in_fits',			'type': 'bool',		'range': None,					'default': True,			'decimalPlaces': None,	'editable': True,	'displayName': 'Write GPS To Fits',			'description': ''},
			{'name': 'fuzz_gps',				'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': True,	'displayName': 'Fuzz GPS',				'description': ''},
			{'name': 'annotation_mag',			'type': 'float',	'range': [0, 20],				'default': 14.0,			'decimalPlaces': 1,	'editable': True,	'displayName': 'Annotation Mag Limit',			'description': ''},
			{'name': 'free_space',				'type': 'int',		'range': [1, 50],				'default': 10,				'decimalPlaces': None,	'editable': True,	'displayName': 'Min Free Drive Space GB',			'description': ''},
		]},

		{'group': 'hidden', 'settings': [
			{'name': 'privacy_notice',			'type': 'int',		'range': None,					'default': 3,				'decimalPlaces': None,	'editable': False,	'displayName': 'Privacy Notice Counter',		'description': ''},
			{'name': 'slow_usb_drive',			'type': 'bool',		'range': None,					'default': False,			'decimalPlaces': None,	'editable': False,	'displayName': 'Slow USB Drive',			'description': ''},
			{'name': 'stretch_method',			'type': 'int',		'range': None,					'default': 5,				'decimalPlaces': None,	'editable': False,	'displayName': 'Stretch Method',			'description': ''},
			{'name': 'version',				'type': 'str',		'range': None,					'default': '',				'decimalPlaces': None,	'editable': False,	'displayName': 'Astrid Version',			'description': ''},
		]},
	]



	def __init__(self, settings_folder, astrid_drive, configs_folder):
		self.processLogger = ProcessLogger.getInstance()
		if self.processLogger is None:
			self.logger = logging.getLogger()
		else:
			self.logger = self.processLogger.getLogger()

		Settings.settings_folder = settings_folder
		Settings.configs_folder = configs_folder

		Settings.__instance = self
		self.read()

		self.astrid_drive = astrid_drive
		self.predictions_folder = self.astrid_drive + '/predictions'


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
		for subsetting in Settings.subsettings:
			if subsetting['name'] == setting_name:
				break

		# Find the group
		group_settings = None
		for usetting in Settings.user_settings:
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


	def isZeroLengthFile(cls, fname):
		return True if os.path.getsize(fname) == 0 else False


	def read(self):
		for subsetting in Settings.subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			self.logger.info('reading settings: %s' % settings_fname)

			if os.path.isfile(settings_fname):
				if self.isZeroLengthFile(settings_fname):
					backup_fname = settings_fname + '.backup'
					if os.path.isfile(backup_fname):
						os.remove(settings_fname)
						os.rename(backup_fname, settings_fname)
						QMessageBox.warning(None, ' ', 'Config file %s was corrupted, this has been repaired from a backup. Please check settings are correct.' % settings_fname, QMessageBox.Ok)
					else:
						QMessageBox.critical(None, ' ', 'Config file %s is zero length, unable to load settings.\n\nAstrid will now exit, you then need to repair or delete this config file to reset to defaults.' % settings_fname, QMessageBox.Ok)
						raise ValueError('Quitting Astrid due to zero length config file: %s !' % settings_fname)

				with open(settings_fname, 'r') as fp:
					setattr(self, subsetting['name'], json.load(fp))
			else:
				setattr(self, subsetting['name'], {})

			self.__updateSettings(subsetting['name'], subsetting)


	def unableToWriteConfigFile(self, fname):
		QMessageBox.critical(None, ' ', 'Unable to write config file %s.\n\nThis is likely due to the USB Drive being full.\n\nShutdown Astrid, clear some video/photos from the USB drive and empty the Trash / Recycle Bin, then startup Astrid.\n\nAstrid will then attempt to recover the prior version of the config file automatically.' % fname, QMessageBox.Ok)
		raise ValueError('Quitting Astrid due to zero length config file: %s !' % fname)


	def write(self):
		for subsetting in Settings.subsettings:
			settings_fname = self.__getSettingsFname(subsetting)
			self.logger.info('Writing settings: %s' % settings_fname)

			# Backup settings file
			backup_fname = settings_fname + '.backup'
			os.rename(settings_fname, backup_fname)
			
			with open(settings_fname, 'w') as fp:
				json.dump(getattr(self, subsetting['name']), fp)

			if self.isZeroLengthFile(settings_fname):
				self.unableToWriteConfigFile(settings_fname)
			else:
				os.remove(backup_fname)


	def writeSubsetting(self, subsetting):
		settings_fname = None
		for s in Settings.subsettings:
			if s['name'] == subsetting:
				settings_fname = self.__getSettingsFname(s)
		if settings_fname is None:
			raise ValueError('no subsetting %s found' % subsetting)

		self.logger.info('Writing settings: %s' % settings_fname)

		jstr = json.dumps(getattr(self, subsetting), indent=4)

		# Backup settings file
		backup_fname = settings_fname + '.backup'
		os.rename(settings_fname, backup_fname)
		
		with open(settings_fname, 'w') as fp:
			fp.write(jstr)
			fp.write('\n')

		if self.isZeroLengthFile(settings_fname):
			self.unableToWriteConfigFile(settings_fname)
		else:
			os.remove(backup_fname)
