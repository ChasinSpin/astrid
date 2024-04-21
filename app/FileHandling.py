import os
import numpy as np
from enum import IntEnum
from astropy.io import fits
from datetime import datetime
from astutils import AstUtils
from settings import Settings
from astsite import AstSite



class FileHandlingImageType(IntEnum):
	VIDEO			= 0
	PHOTO_LIGHT		= 1
	PHOTO_BIAS		= 2
	PHOTO_DARK		= 3
	PHOTO_FLAT		= 4
	PHOTO_POLAR_ALIGN	= 5



class FileHandling:

	def __init__(self, baseFolder, target, fileHandlingType, startingSequence=0):
		self.baseFolder		= baseFolder
		self.sequence		= startingSequence
		self.target		= target
		self.fileHandlingType	= fileHandlingType
		self.fhTypes		= ['Video', 'Light', 'Bias', 'Dark', 'Flat', 'PolarAlign']
		self.prepend		= None


	def setTarget(self, target):
		self.target		= target
		self.sequence		= 0


	# Prepend "prepend" to the file
	# Set to None for no prepend

	def setPrepend(self, prepend):
		self.prepend = prepend


	# Returns the next file name, checking to see if the file exists (in which case it increments the sequence num)
	# and creates the folders to the destination

	def __getFilename(self, extension):

		while True:
			prepend_target = self.target
			if self.prepend is not None:
				prepend_target += '_' + self.prepend

			fname = self.baseFolder + '/' + \
				self.fhTypes[self.fileHandlingType] + '/' +  \
				prepend_target + ('_%04d' % self.sequence) + '.' + extension

			if os.path.exists(fname):
				self.sequence += 1
				continue

			# Make the folders in the path if they don't exist
			folders = os.path.dirname(fname)
			os.makedirs(folders, mode=0o777, exist_ok=True)

			break
			
		return fname


	def __decimalDegreesToDMS(self, deg):
		# Converts decimal degrees to dms for lat/lon
		d = int(deg)
		mins = (deg - d) * 60.0
		m = int(mins)
		s = (mins - m) * 60.0

		m = abs(m)
		s = abs(s)

		return (d, m, s)
		

	def save_photo_dng(self, request, metadata):
		fname = self.__getFilename('dng')
		print("Saving:", fname)
		request.save_dng(fname)
		self.sequence += 1

	
	# ra, dec are in JNow, and ra is in mount format (24h)

	def save_photo_fit(self, arr, metadata, sensorMode, sensorModeExtra, obsDateTime, focalLen, position):
		fname = self.__getFilename('fit')
		print("Saving:", fname)

		reshape_width	= int(arr.shape[1]/2)
		reshape_height	= arr.shape[0]

		# Convert from 8 bit buffer to 16 bit values
		arr = np.frombuffer(arr, dtype=np.uint16)

		# Reshape to the correct width/height after converting from 8 to 16 bit values
		arr = np.reshape(arr, (reshape_height, reshape_width))
		print('UInt16 Min:', np.min(arr))
		print('UInt16 Max:', np.max(arr))
		print('UInt16 Mean:', np.mean(arr))

		# Convert to float32 as fits doesn't support unsigned 16 bit
		#arr = arr.astype('float32')
		#print('Float32 Min:', np.min(arr))
		#print('Float32 Max:', np.max(arr))
		#print('Float32 Mean:', np.mean(arr))

		# The image is larger in the X direction than the number of pixels, due to stride, fix this
		arr = arr[0:sensorMode['size'][1], 0:sensorMode['size'][0]]

		#arr = np.flipud(arr)

		# Figure out bayer order
		bayer = sensorMode['unpacked']
		#bayer = bayer[1:5]
		if bayer == 'R10':
			bayer = None
		else:
			bayer = 'BGGR'
		print(bayer)

		hdu = fits.PrimaryHDU(arr)
		hdul = fits.HDUList([hdu])

		hdr = hdul[0].header

		hdr['INSTRUME']	= 'Astrid:' + sensorModeExtra['model']
		hdr['OBJECT']	= self.target
		hdr['TELESCOP']	= AstUtils.selectedConfigName()
		hdr['EXPTIME']	= metadata['ExposureTime'] / 1000000.0
		hdr['XPIXSZ']	= sensorModeExtra['pixelSize'][0]
		hdr['YPIXSZ']	= sensorModeExtra['pixelSize'][1]
		hdr['XBINNING']	= sensorModeExtra['bining']
		hdr['YBINNING']	= sensorModeExtra['bining']
		hdr['FOCALLEN']	= focalLen
		hdr['CCD-TEMP']	= 0.0
		hdr['FILTER']	= 'NONE' 
		hdr['IMAGETYP']	= self.fhTypes[self.fileHandlingType]
		hdr['GAIN']	= metadata['AnalogueGain']
		hdr['OFFSET']	= 0
		hdr['CVF']	= 0.0
		hdr['PROGRAM']	= 'Astrid'
		if Settings.getInstance().general['location_in_fits']:
			(d, m, s) = self.__decimalDegreesToDMS(AstSite.lat)
			hdr['SITELAT']	= '%3d %02d %0.3f' % (d, m, s)
			(d, m, s) = self.__decimalDegreesToDMS(AstSite.lon)
			hdr['SITELONG']	= '%3d %02d %0.3f' % (d, m, s)
	
		if position is None:
			(ra, dec) = (0.0, 0.0)
		else:
			(ra, dec) = position.raDec360Deg('fk5')
		hdr['RA']	= ra
		hdr['DEC']	= dec
		if bayer is not None:
			hdr['BAYERPAT']	= bayer
			hdr['XBAYROFF'] = 0
			hdr['YBAYROFF'] = 0
		hdr['BSCALE']	= 1.0
		hdr['BZERO']	= 32768.0
		file_creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
		obs_time = obsDateTime.strftime("%Y-%m-%dT%H:%M:%S")
		hdr['DATE']	= file_creation_time		# Time of file creation UTC
		hdr['DATE-OBS']	= obs_time			# Start Time of the observation UTC
		hdr['ROWORDER'] = 'TOP-DOWN'			# Siril Request - Reference: https://free-astro.org/index.php?title=Siril:FITS_orientation

		print(repr(hdu.header))

		hdul.writeto(fname)
		hdul.close()
		self.sequence += 1

		aduMax = int(pow(2, sensorMode['bit_depth']))
		print("aduMax:", aduMax)
		print("Histogram:")
		hist = np.histogram(arr, 20, (0.0, float(aduMax)), density=True)
		for i in range(len(hist[0])):
			print("%04d: %0.8f" % ((hist[1][i] + hist[1][i+1])/2.0, hist[0][i]))

		return fname
