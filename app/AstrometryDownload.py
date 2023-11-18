from processlogger import ProcessLogger
import os
import logging
import requests
from settings import Settings

class AstrometryDownload:
	series = [
		{ 'fovWidth':6.25,	'suggestedIndexFov':[2.0, 2.8],		'indexScale':'0',	'seriesName':'5200', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5200-'	},
		{ 'fovWidth':10.0,	'suggestedIndexFov':[2.8, 4.0],		'indexScale':'1',	'seriesName':'5201', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5201-'	},
		{ 'fovWidth':14.0,	'suggestedIndexFov':[4.0, 5.6],		'indexScale':'2',	'seriesName':'5202', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5202-'	},
		{ 'fovWidth':20.0,	'suggestedIndexFov':[5.6, 8.0],		'indexScale':'3',	'seriesName':'5203', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5203-'	},
		{ 'fovWidth':27.5,	'suggestedIndexFov':[8,   11],		'indexScale':'4',	'seriesName':'5204', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5204-'	},
		{ 'fovWidth':40.0,	'suggestedIndexFov':[11,  16],		'indexScale':'5',	'seriesName':'5205', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5205-'	},
		{ 'fovWidth':55.0,	'suggestedIndexFov':[16,  22],		'indexScale':'6',	'seriesName':'5206', 'seriesFileNumberRange':[0, 47],		'seriesURL':'https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/',	'seriesFileStem':'index-5206-'	},
		{ 'fovWidth':5000.0,	'suggestedIndexFov':[22,  2000],	'indexScale':'7-19',	'seriesName':'4100', 'seriesFileNumberRange':[7, 19],		'seriesURL':'http://data.astrometry.net/4100/',						'seriesFileStem':'index-41'	},
	]



	def __init__(self, astrid_drive, focal_length: float, frame_width_mm: float):
		self.processLogger = ProcessLogger.getInstance()
		if self.processLogger is None:
			self.logger = logging.getLogger()
		else:
			self.logger = self.processLogger.getLogger()

		series = AstrometryDownload.series
		self.astrid_drive = astrid_drive

		fov_arcmin = ((57.3 / focal_length) * frame_width_mm) * 60.0
		self.logger.info('fov(width): %0.3f arcmin' % fov_arcmin)

		# Determine the series indexes required
		seriesIndexes = []

		# Find the matching series index
		ind = None
		for i in range(len(series)):
			if fov_arcmin < series[i]['fovWidth']:
				ind = i
				break
		if ind is None:
			raise ValueError('AstrometryDownload: focal length or camera settings are out of range for Astrometry, check focal length')

		seriesIndexes.append(ind)
		if series[ind]['seriesName'] != '4100':
			seriesIndexes.append(len(series)-1)

		self.seriesUrls = []
		for i in seriesIndexes:
			self.logger.info('platesolving needs %s' % series[i]['seriesName'])
			self.seriesUrls.append(self.__generateURLsForSeriesIndex(i))


	def generateAstrometryCfg(self) -> str:
		"""
			Generates a temporary astrometry.cfg file given a focal length and returns it
		"""
		astrometryCfg = '/tmp/astrid_astrometry.cfg'
		
		# Now we add these series to astrometry.cfg in the config
		addPath = ''
		for sUrls in self.seriesUrls:
			series_folder = os.path.dirname(sUrls[0]['filename'])
			addPath += 'add_path %s\n' % series_folder

		with open('/home/pi/astrid/app/astrometry.cfg', 'r') as file:
			txt = file.read()
			txt = txt.replace('ADD_PATH', addPath)

		with open(astrometryCfg, 'w') as file:
			file.write(txt)

		return astrometryCfg


	def astrometryFilesArePresent(self):
		""" Checks the required astrometry files are present, returns True if they are """
		for sUrls in self.seriesUrls:
			for url in sUrls:
				if not os.path.exists(url['filename']):
					return False

		return True



	def download(self, callback):
		""" Downloads Astrometry Files, returns True on success """
		for sUrls in self.seriesUrls:
			for url in sUrls:
				if not self.__downloadUrl(url['url'], url['filename'], callback):
					return False

		return True



	def __downloadUrl(self, url, fname, callback):
		series_folder = os.path.dirname(fname)
		if not os.path.isdir(series_folder):
			os.mkdir(series_folder)

		#self.logger.info('url:%s fname:%s' % (url, fname))
		if not os.path.exists(fname):
			try:
				with requests.get(url, stream=True, timeout=5) as response:
					if response is not None and 'Content-length' in response.headers:
						chunk_count = 0
						chunk_size = 10*1024
						file_size = int(response.headers['Content-length'])
						with open(fname, mode='wb') as file:
							for chunk in response.iter_content(chunk_size=chunk_size):
								chunk_count += 1
								percent_downloaded = (chunk_count * chunk_size) / file_size
								if percent_downloaded > 1.0:
									percent_downloaded = 1.0
								callback(percent_downloaded * 100, fname)
								#print('\rDownloading: %s %0.0f%%' % (fname, (percent_downloaded * 100.0)), end='') 	
								file.write(chunk)
						#print('\rDownloading: %s complete                                        ' % fname)
			except requests.ConnectionError:
				self.logger.error('Failed to download: %s' % url)
				return False

		return True



	def __generateURLsForSeriesIndex(self, seriesIndex: int) -> [dict]:
		""" Generates a list of download files for seriesIndex """
		config = AstrometryDownload.series[seriesIndex]
		urlList = []
		fileNumberRange = config['seriesFileNumberRange']

		for i in range(fileNumberRange[0], fileNumberRange[1] + 1):
			fname = '%s%02d.fits' % (config['seriesFileStem'], i)
			full_fname = '%s/astrometry/%s/%s' % (self.astrid_drive, config['seriesName'], fname)
			dict = { 'url':'%s%s' % (config['seriesURL'], fname), 'filename': full_fname }
			urlList.append(dict)

		return urlList
