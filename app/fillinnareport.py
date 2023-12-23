from openpyxl import load_workbook
from settings import Settings
from datetime import datetime



class FillInNAReport():

	MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

	def __init__(self, fname, required_metadata, user_metadata, started_observing, stopped_observing):
		super().__init__()
		self.user_metadata = user_metadata
		self.required_metadata = required_metadata
		self.started_utc = started_observing
		self.stopped_utc = stopped_observing

		wb = load_workbook(fname)

		self.sheet = wb['DATA']

		# Validate that we have a proper Asteroid Occultation Report FOrm
		if not self.sheet['G1'].value == 'Asteroid Occultation Report Form':
			raise ValueError('North American Occultation Report Form Is Not Valid')

		self.__update_cells()

		wb.save(fname)


	def __get_metadata(self, entry_type, key):
		value = None

		if entry_type == 'user':
			metadata = self.user_metadata
		elif entry_type == 'required':
			metadata = self.required_metadata
		else:
			raise ValueError('Unrecognized metadata entry type')


		# Find the value for the key
		for entry in metadata:
			if entry[0] == key:
				if entry_type == 'user':
					value = entry[2]
				else:
					value = entry[1]
				break

		if value is None or (isinstance(value, str) and len(value) == 0): 
			return None

		return value


	def __fill_value(self, cell, entry_type, key):
		value = self.__get_metadata(entry_type, key)
		if value is not None:
			self.sheet[cell] = value
			
	
	def __update_cells(self):
		cell_mapping = {
			'AstNum':			'E7',
			'AstName':			'K7',
			'EventYear':			'D5',
			'EventMonth':			'K5',
			'EventDay':			'P5',
			'StarCatalog':			'S7',
			'StarNumber':			'X7',
			'PredictedHours':		'Y5',
			'PredictedMinutes':		'AA5',
			'PredictedSeconds':		'AC5',
			'LatitudeFormat':		'E17',
			'LongitudeFormat':		'N17',
			'Latitude':			'E18',
			'LatitudeDir':			'J18',
			'Longitude':			'N18',
			'LongitudeDir':			'R18',
			'Elevation':			'V18',
			'ElevationUnits':		'W18',
			'ElevationDatum':		'AA18',
			'Timing':			'E22',
			'TimingDevice':			'E23',
			'Detector':			'E25',
			'OtherDetectorRelatedInfo':	'V25',
			'ObserverName':			'D9',
			'ObserverEmail':		'S9',
			'Aperture':			'E20',
			'ApertureUnits':		'H20',
			'FocalRatio':			'L20',
			'TelescopeType':		'T20',
			'StartedObservingHours':	'F31',
			'StartedObservingMins':		'H31',
			'StartedObservingSecs':		'J31',
			'StoppedObservingHours':	'F37',
			'StoppedObservingMins':		'H37',
			'StoppedObservingSecs':		'J37',
			'VideoFormat':			'L25',
			'ExposureIntegration':		'P25',
		}

		for key in cell_mapping.keys():
			cell = cell_mapping[key]
			if   key == 'AstNum':
				self.__fill_value(cell, 'user', 'OCCULTATION-OBJECT-NUMBER')
			elif key == 'AstName':
				self.__fill_value(cell, 'user', 'OCCULTATION-OBJECT-NAME')
			elif key == 'EventYear':
				predicted_time = self.__get_metadata('user', 'OCCULTATION-PREDICTED-CENTER-TIME')
				if predicted_time is not None:
					predicted_time					= datetime.strptime(predicted_time, '%Y-%m-%dT%H:%M:%S')
					self.sheet[cell_mapping['EventYear']]		= predicted_time.year
					self.sheet[cell_mapping['EventMonth']]		= self.MONTHS[predicted_time.month-1]
					self.sheet[cell_mapping['EventDay']]		= predicted_time.day
					self.sheet[cell_mapping['PredictedHours']]	= '%02d' % predicted_time.hour
					self.sheet[cell_mapping['PredictedMinutes']]	= '%02d' % predicted_time.minute
					self.sheet[cell_mapping['PredictedSeconds']]	= '%02d' % predicted_time.second
			elif key == 'StarCatalog':
				star = self.__get_metadata('user', 'OCCULTATION-STAR')
				if star is not None:
					starCatalog = None
					starNumber = None
					if star.startswith('TYC'):
						starCatalog = 'TYC       xxxx-xxxxx-x'
						starNumber = star.replace('TYC ', '')
					elif star.startswith('HIP'):
						starCatalog = 'HIP  xxxxxx'
						starNumber = star.replace('HIP ', '')
					elif star.startswith('UCAC2'):
						starCatalog = 'UCAC2        xxxxxxxx'
						starNumber = star.replace('UCAC2 ', '')
					elif star.startswith('UCAC3'):
						starCatalog = 'UCAC3     xxx - xxxxxx'
						starNumber = star.replace('UCAC3 ', '')
					elif star.startswith('UCAC4'):
						starCatalog = 'UCAC4     xxx - xxxxxx'
						starNumber = star.replace('UCAC4 ', '')
					elif star.startswith('G'):
						starCatalog = 'G-coords hhmmss.s?ddmmss'
						starNumber = star.replace('G', '')
					elif star.startswith('URAT1'):
						starCatalog = 'URAT1    xxx - xxxxxxx'
						starNumber = star.replace('URAT1 ', '')
					elif star.startswith('1B'):
						starCatalog = '1B    xxx - xxxxxxx'
						starNumber = star.replace('1B ', '')
					elif star.startswith('1N'):
						starCatalog = '1N    xxx - xxxxxxx'
						starNumber = star.replace('1N ', '')

					if starCatalog is not None and starNumber is not None:
						self.sheet[cell_mapping['StarCatalog']] = starCatalog
						self.sheet[cell_mapping['StarNumber']] = starNumber
			elif key == 'Latitude':
				latitude = self.__get_metadata('required', 'LATITUDE')
				if latitude is not None:
					self.sheet[cell_mapping['LatitudeFormat']] = 'deg.ddddd'
					latitude = float(latitude)
					self.sheet[cell_mapping['Latitude']] = '%0.5f' % abs(latitude)
					self.sheet[cell_mapping['LatitudeDir']] = 'S' if latitude < 0 else 'N'
			elif key == 'Longitude':
				longitude = self.__get_metadata('required', 'LONGITUDE')
				if longitude is not None:
					self.sheet[cell_mapping['LongitudeFormat']] = 'deg.ddddd'
					longitude = float(longitude)
					self.sheet[cell_mapping['Longitude']] = '%0.5f' % abs(longitude)
					self.sheet[cell_mapping['LongitudeDir']] = 'W' if longitude < 0 else 'E'
			elif key == 'Elevation':
				altitude = self.__get_metadata('required', 'ALTITUDE')
				if altitude is not None:
					altitude = float(altitude)
					self.sheet[cell_mapping['Elevation']] = '%0.1f' % altitude
					self.sheet[cell_mapping['ElevationUnits']] = 'm'
					self.sheet[cell_mapping['ElevationDatum']] = 'WGS84'
			elif key == 'Timing':
				self.sheet[cell_mapping[key]] = 'GPS - other linking'
			elif key == 'TimingDevice':
				self.sheet[cell_mapping[key]] = 'ASTRID'
			elif key == 'Detector':
				self.sheet[cell_mapping[key]] = 'ASTRID'
			elif key == 'OtherDetectorRelatedInfo':
				sensor = self.__get_metadata('required', 'INSTRUMENT-SENSOR')
				gain   = self.__get_metadata('required', 'INSTRUMENT-GAIN')
				if sensor is not None and gain is not None:
					self.sheet[cell_mapping['OtherDetectorRelatedInfo']] = 'ASTRID %s Mono Gain %s' % (sensor, gain)
			elif key == 'ObserverName':
				self.__fill_value(cell, 'required', 'OBSERVER')
			elif key == 'ObserverEmail':
				self.__fill_value(cell, 'required', 'OBSERVER-ID')
			elif key == 'Aperture':
				aperture	= self.__get_metadata('user', 'INSTRUMENT-APERTURE')
				focalLength	= self.__get_metadata('user', 'FOCAL-LENGTH')
				if aperture is not None and focalLength is not None and aperture > 0:
					aperture = float(aperture)
					focalLength = float(focalLength)
					self.sheet[cell_mapping['Aperture']] = '%0.1f' % (aperture / 10.0)
					self.sheet[cell_mapping['ApertureUnits']] = 'cm'
					focalRatio = focalLength / aperture
					self.sheet[cell_mapping['FocalRatio']] = '%0.1f' % focalRatio
			elif key == 'TelescopeType':
				self.__fill_value(cell, 'user', 'INSTRUMENT-OPTICAL-TYPE')
			elif key == 'StartedObservingHours':
				self.sheet[cell_mapping['StartedObservingHours']] = '%02d' % self.started_utc[0]
				self.sheet[cell_mapping['StartedObservingMins']] = '%02d' % self.started_utc[1]
				self.sheet[cell_mapping['StartedObservingSecs']] = '%02.3f' % self.started_utc[2]
			elif key == 'StoppedObservingHours':
				self.sheet[cell_mapping['StoppedObservingHours']] = '%02d' % self.stopped_utc[0]
				self.sheet[cell_mapping['StoppedObservingMins']] = '%02d' % self.stopped_utc[1]
				self.sheet[cell_mapping['StoppedObservingSecs']] = '%02.3f' % self.stopped_utc[2]
			elif key == 'VideoFormat':
				self.sheet[cell_mapping[key]] = 'ADVS'
			elif key == 'ExposureIntegration':
				self.sheet[cell_mapping[key]] = 'Other'
