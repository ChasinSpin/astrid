from processlogger import ProcessLogger
import sys
import cv2
from datetime import datetime
from pprint import *
from picamera2 import Picamera2, MappedArray, Controls
import picamera2.formats as formats
from picamera2.encoders import Encoder
from libcamera import Transform, controls
from picamera2.previews.qt import QGlPicamera2, QPicamera2
from settings import Settings
from FileHandling import *
from enum import Enum
import copy
import time
from datetime import datetime, timezone, timedelta
from PlateSolver import *
from PolarAlign import *
import random
import string
import IndiDevices
from astropy.coordinates import FK5, SkyCoord
from astropy.time import Time
import astropy.units as u
from astropy.io import fits
from astsite import AstSite
from astcoord import AstCoord
from ravf_encoder import RavfEncoder, RavfImageFormat, RavfColorType
from UiPanelConnectFailedIndi import UiPanelConnectFailedIndi
from UiPanelAstrometry import UiPanelAstrometry
from UiDialogPanel import UiDialogPanel
from astropy.stats import sigma_clipped_stats
#from photutils.detection import DAOStarFinder
from photutils.detection import IRAFStarFinder
from PyQt5.QtWidgets import QMessageBox
from AstrometryDownload import AstrometryDownload
import logging
#import gc


pa_test_images_folder = '/home/pi/astrid/app/pa_test_images/'
VIDEO_BUFFER_COUNT = 12

# Some Rules:
#	1. We must also have a main stream, so we use that for the preview
#	2. Picamera2 can only provide:
#		Main:  XBGR8888, XRGB8888, RGB888, BGR888, YUV420 (debayered) 8-bit only
#		Lores: YUV420 (debayered)
#		Raw:   Camera specific (not debayered) 10 or 12 bit too
#	3. Unpacking raw streams, is too slow
#
#	I.E.: Because we want full bit depth for quantizing brightness, we are required to use Raw for still and video recording
#	which means we need to debayer.  Pixinsight will handler the debayering for us for stills
#
# This means we use the following configuration:
# 	Preview Configuration 
#		Stream Main:	Preview (size=preview graphics size)
#		Stream Raw:	Unused, encode=None
#	Video Configuration
#		Stream Main:	Preview (size=preview graphics size)
#		Stream Raw:	Null Encoder to file
# 	Still Configuration
#		Stream Main:	Only used to quickly process
#		Stream Raw:	Saved to Fits, encode=None
#
# Therefore:
#	buffer_count	= 6 	 	# so we can handle anything up to video speeds
#	queue		= False		# We want frames on time
#	display		= "main"	# Display the main stream in the preview window
#	encode		= "raw"		# We only ever encode the raw stream for video, can also be None for preview or still
#	lores		= None		# We never want a lores stream


class OperatingMode(Enum):
	PHOTO		= 1
	POLAR_ALIGN	= 2
	OTE_VIDEO	= 3
	VIDEO		= 4

class OperatingVideoMode(Enum):
	PREVIEW	  = 3 
	RECORDING = 4

class OperatingPhotoMode(Enum):
	IDLE		   = 5
	RECORDING_SEQUENCE = 6
	RECORDING_SINGLE   = 7


class CameraModel:

	# Determines the size of the sensor (full frame), based on
	# scanning through all available raw sensor modes looking for the largest
	# X and Y
	def __getFullFrameSize(self):
		ret	= [0,0]
		for i in range(len(self.sensor_modes)):
			size = self.sensor_modes[i]['size']
			crop = self.sensor_modes[i]['crop_limits']
			cropSize = (crop[2], crop[3])
			ret[0] = max(size[0], cropSize[0], ret[0])
			ret[1] = max(size[1], cropSize[1], ret[1])
		return (ret[0], ret[1])


	# Configures the camera for 2 streams:
	#	main = preview
	#	raw = recording

	def __configureCameraStreams(self):
		# Configure "raw" stream for recording and "main" stream for preview
		video_raw_mode = copy.deepcopy(self.__cameraSelectedMode())

		# If we have a 10 or 12 bit packed format, instruct to unpack
		# for video mode only
		video_raw_mode = copy.deepcopy(self.__cameraSelectedMode())
		if str(video_raw_mode['format']) == 'SRGGB12_CSI2P':
			#video_raw_mode['format'] = 'SBGGR12_CSI2P'
			video_raw_mode['format'] = 'SBGGR12'
		if str(video_raw_mode['format']) == 'SRGGB10_CSI2P':
			video_raw_mode['format'] = 'SBGGR10_CSI2P'
			#video_raw_mode['format'] = 'SBGGR10'
		if str(video_raw_mode['format']) == 'R10_CSI2P':
			video_raw_mode['format'] = 'R10_CSI2P'

		# If we have a 10 or 12 bit packed format, instruct to unpack
		# for still mode only
		still_raw_mode = copy.deepcopy(self.__cameraSelectedMode())
		if str(still_raw_mode['format']) == 'SRGGB12_CSI2P':
			still_raw_mode['format'] = 'SBGGR12'
		if str(still_raw_mode['format']) == 'SRGGB10_CSI2P':
			still_raw_mode['format'] = 'SBGGR10'
		if str(still_raw_mode['format']) == 'R10_CSI2P':
			still_raw_mode['format'] = 'R10'

		self.videoFrameDuration = 100000 	#10 fps
		self.picam2_video_config = self.picam2.create_preview_configuration(
			main={"size": (self.previewWidth, self.previewHeight) }, 
			lores=None,
			display="main",
			queue=False,
			raw=video_raw_mode,
			encode="raw",
			buffer_count=self.videoBufferCount,
			controls=self.__defaultAstroControls(self.videoFrameDuration))

		self.picam2_still_config = self.picam2.create_preview_configuration(
			main={"size": (self.previewWidth, self.previewHeight) }, 
			lores=None,
			display="main",
			queue=False,
			raw=still_raw_mode,
			encode=None,
			buffer_count=1,
			controls=self.__defaultAstroControls(5000000))	# Default photo exposure

		# Align this configuration we desired with the capabilities of the hardware
		# (this may change some settings we've requested
		self.picam2.align_configuration(self.picam2_video_config)
		self.picam2.align_configuration(self.picam2_still_config)

		# Configure the camera stream
		self.picam2.configure(self.picam2_still_config)


	# Returns a set of the camera controls for a configuration
	
	def __defaultAstroControls(self, frameDuration):
		return {
				'AeEnable':		False,
				'AnalogueGain':		self.settings['gain'],
				'AwbEnable':		False,
				'Brightness':		0.0,
				'Contrast':		1.0,
				'NoiseReductionMode':	controls.draft.NoiseReductionModeEnum.Off,
				'Saturation':		1.0,
				'Sharpness':		0.0,
				'FrameDurationLimits':	(frameDuration, frameDuration),
				'ExposureTime':		frameDuration
			}


	def configureVideoFrameDuration(self, frameDuration):
		self.videoFrameDuration = frameDuration

		self.picam2_video_config['controls']['FrameDurationLimits'] = (self.videoFrameDuration, self.videoFrameDuration)
		self.picam2_video_config['controls']['ExposureTime']	    = self.videoFrameDuration

		if self.operatingMode == OperatingMode.OTE_VIDEO:
			# Update the live config
			self.picam2.controls.FrameDurationLimits = (self.videoFrameDuration, self.videoFrameDuration)
			self.picam2.controls.ExposureTime 	 = self.videoFrameDuration



	def configureVideoFrameRate(self, frameRate):
		if frameRate == 0:
			self.videoFrameDuration = 0
		else:
			self.videoFrameDuration = int((1.0 / frameRate) * 1000000.0)

		self.picam2_video_config['controls']['FrameDurationLimits'] = (self.videoFrameDuration, self.videoFrameDuration)
		self.picam2_video_config['controls']['ExposureTime']	    = self.videoFrameDuration

		if self.operatingMode == OperatingMode.OTE_VIDEO:
			# Update the live config
			self.picam2.controls.FrameDurationLimits = (self.videoFrameDuration, self.videoFrameDuration)
			self.picam2.controls.ExposureTime 	 = self.videoFrameDuration

			# Now flush the queue
			self.picam2.stop()
			self.picam2.start()


	def configureStillExposureTime(self, expSecs):
		if expSecs == 0.0:
			expSecs = 0.1
			self.filePlateSolve = True
		else:
			self.filePlateSolve = False	
		frameDuration = int(expSecs * 1000000.0)
		self.picam2_still_config['controls']['FrameDurationLimits'] = (frameDuration, frameDuration)
		self.picam2_still_config['controls']['ExposureTime']	    = frameDuration
		if self.operatingMode == OperatingMode.PHOTO or self.operatingMode == OperatingMode.POLAR_ALIGN:
			print("Updating exposure time to:", frameDuration)
			#self.picam2.controls.ExposureTime 	 = frameDuration
			self.picam2.configure(self.picam2_still_config)


	# Creates the preview
	# acclerated_render = True  - Faster rendering (but not VNC etc. compatible)

	def __createPreview(self):
		hflip	  = self.settings['hflip']
		vflip	  = self.settings['vflip']
		transform = Transform(hflip=hflip, vflip=vflip)

		if self.settings['accelerated_preview']:
			print("Configuring Accelerated Preview")
			self.qt_picamera = QGlPicamera2(self.picam2, width=self.previewWidth, height=self.previewHeight, keep_ar=True, transform=transform)
		else:
			print("Configuring Non-Accelerated Preview")
			self.qt_picamera = QPicamera2(self.picam2, width=self.previewWidth, height=self.previewHeight, keep_ar=True, transform=transform)


	# Display information about the configuration

	def __dumpConfiguration(self):
		# Display camera properties
		print("Camera Properties:")
		pprint(self.picam2.camera_properties)
		print()

		# Displays camera configuration
		print("Camera Video Config:");
		pprint(self.picam2_video_config)
		print()
		print("Camera Still Config:");
		pprint(self.picam2_still_config)
		print()
		print("Full Frame Size:", self.full_frame_size)
		print()
		print("Camera Controls:", self.picam2.camera_controls)
		print()

		# Display available sensor modes
		print("Available Sensor Modes:")
		for i in range(len(self.sensor_modes)):
			mode = self.sensor_modes[i]
			fov = self.__modeFieldOfViewPercentage(mode)
			print("Mode:%d Size:(%d,%d) Bin:%d Bits:%d FOV:(%0.1f%%,%0.1f%%) MaxFPS:%0.2f Exp:%d->%dus Format:%s Unpacked:%s" % (i, mode['size'][0], mode['size'][1], self.__modeBinSize(mode), mode['bit_depth'], fov[0], fov[1], mode['fps'], mode['exposure_limits'][0], mode['exposure_limits'][1], mode['format'], mode['unpacked']))
		print()


	def garbageCollectionNotification(self, phase, info):
		print('**** Garbage Collection:', phase)

	def __init__(self, previewWidth, previewHeight, splashScreen):
		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()
		self.logger.debug('CameraModel started')

		#gc.callbacks = [self.garbageCollectionNotification]
		#gc.set_debug(gc.DEBUG_STATS)
		self.ui			= None
		self.settings		= Settings.getInstance().camera
		settings_site = Settings.getInstance().site
		if len(settings_site.keys()) > 0:
			AstSite.set(settings_site['name'], settings_site['latitude'], settings_site['longitude'], settings_site['altitude'])
		else:
			AstSite.set('Unknown', 0.00001, 0.00001, 0.0)

		self.filePlateSolve	= False
		self.plateSolverThread	= None	
		self.polarAlignStep	= 0
		self.polarAlignTestIndex= 3
		self.photoCountTotal	= 1
		self.photoCountCurrent	= 1
		self.lastMountCoords	= None
		self.dithering		= False
		self.objectCoords	= None
		self.lastCoords		= None
		self.autostretch	= False
		self.zebras		= False
		self.crosshairs		= False
		self.stardetection	= False
		self.videoTarget	= 'None'
		self.search_full_sky	= False
		self.trackingActivatedNotify = False
		self.paSolver		= None
		self.autoStretchLower	= 5.0
		self.autoStretchUpper	= 30.0
		self.photoCallback	= None
		self.platesolveCallback	= None
		self.videoBufferCount	= VIDEO_BUFFER_COUNT
		self.plannedAutoShutdown= False

		#Picamera2.set_logging(Picamera2.DEBUG)

		splashScreen.setMessage('Please wait: Setting up mount...')
		self.indi		= IndiDevices.IndiDevices()
		self.indi_usb_tty	= Settings.getInstance().mount['indi_usb_tty']
		self.simulate		= False
		while not self.indi.connect(self.indi_usb_tty, self.simulate):
			dialog = UiDialogPanel('Failed to connect to mount', UiPanelConnectFailedIndi, args = self)
		self.indi.telescope.setSite(AstSite.lat, AstSite.lon, AstSite.alt)
		self.indi.telescope.setTime(datetime.utcnow(), Settings.getInstance().mount['local_offset'])
		self.indi.telescope.pierSide(west=True)
		self.indi.telescope.setCoordUpdateCallback(self.updateRaDecPos)
		self.indi.telescope.setTrackingUpdateCallback(self.updateTracking)
		if Settings.getInstance().mount['parkmethod'] == 'park':
			self.indi.telescope.setParkUpdateCallback(self.updatePark)

		self.lastFitFile	= "dummy.fit"
		self.lastSolvedPosition = None

		self.photoFileHandling	= FileHandling(self.settings['photosFolder'], 'None', FileHandlingImageType.PHOTO_LIGHT)
		self.fileHandling	= self.photoFileHandling

		self.operatingMode	= OperatingMode.PHOTO
		self.operatingSubMode	= OperatingPhotoMode.IDLE

		# Load the camera
		self.picam2		= Picamera2()

		# Setup information we need to know about
		self.previewWidth	= previewWidth
		self.previewHeight	= previewHeight
		self.sensor_modes	= self.picam2.sensor_modes
		self.full_frame_size	= self.__getFullFrameSize()

		# Configure things
		splashScreen.setMessage('Please wait: Starting camera...')
		self.__configureCameraStreams()
		self.__createPreview()
		self.configureStillExposureTime(self.settings['default_photo_exposure'])

		# Add overlay
		self.color = (223, 0, 0)
		self.origin = (0, 30)
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.scale = 1
		self.thickness = 2

		# Initialize sensor and frame timestamps
		self.last_sensor_timestamp = 0
		self.last_frame_timestamp = 0.0

		# Setup a callback to called on every frame received (for overlay/timestamping)
		self.picam2.pre_callback = self.__frame_pre_callback

		# Start preview in video mode
		#self.picam2.start()

		self.__dumpConfiguration()

		# Check we have the astrometry files we need, and download if we don't
		frame_width_mm = (self.picam2.camera_properties['UnitCellSize'][0]/1000000.0) * self.full_frame_size[0]
		astrometryDownload = AstrometryDownload(astrid_drive = Settings.getInstance().astrid_drive, focal_length = Settings.getInstance().platesolver['focal_length'], frame_width_mm = frame_width_mm)
		if not astrometryDownload.astrometryFilesArePresent():
			dialog = UiDialogPanel('Astrometry Download', UiPanelAstrometry, args = astrometryDownload)
		astrometryDownload = None



	# Display the timestamp on the frame

	def __frame_pre_callback(self, request):
		request.timestamps = {}

		now = datetime.now(timezone.utc)
		#print('callback:', now)
		request.timestamps['frame_end_datetime'] = now	# Note this is not when the frame capture ended, it's after it's read out

		epoch = datetime(2010, 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo = timezone.utc) # 00:00:00 1st Jan 2010
		seconds_since_epoch  = (now - epoch).total_seconds()
		nanoseconds_since_epoch = int(seconds_since_epoch * 1000000000)
		request.timestamps['frame_end_nanoseconds_since_2010'] = nanoseconds_since_epoch # Note this is not when the frame capture ended, it's after it's read out

		metadata = request.get_metadata()
		#print(request.request)

		start_frame = now - timedelta(seconds = metadata['FrameDuration'] / 1000000)
		request.timestamps['frame_start_datetime'] = start_frame # Note this is not when the frame capture ended, it's after it's read out

		seconds_since_epoch  = (start_frame - epoch).total_seconds()
		nanoseconds_since_epoch = int(seconds_since_epoch * 1000000000)
		request.timestamps['frame_start_nanoseconds_since_2010'] = nanoseconds_since_epoch # Note this is not when the frame capture ended, it's after it's read out
  
		timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
		
		# Display with opencv directly writing display memory
		with MappedArray(request, "main") as m:
			if self.stardetection:
				#full_image = fits.getdata(Settings.getInstance().astrid_drive + '/Photo/Light/None_0209.fit', ext = 0)
				full_image = m.array[:, :, 0]
				
				bkg_mean, bkg_median, bkg_std = sigma_clipped_stats(full_image, sigma=3.0)
				print((bkg_mean, bkg_median, bkg_std))
				#daofind = DAOStarFinder(fwhm=8.0, threshold=bkg_std * 15.0)
				#sources = daofind(full_image - bkg_median)
				iraffind = IRAFStarFinder(threshold=bkg_std * 5.0, fwhm=5.0, exclude_border=True, brightest=40)
				sources = iraffind.find_stars(full_image - bkg_median)
				if sources is not None and sources.colnames is not None:
					for col in sources.colnames:
						if col not in ('id', 'npix'):
							sources[col].info.format = '%0.2f'	# For consistent table output
					sources.pprint(max_width=75)
				
				# Scale to 255	
				display_image = full_image.astype(np.float32)
				display_image *= 255.0/1023.0
				display_image = display_image.astype(np.uint8)

				# Resize to watch screen display size
				src_height = full_image.shape[0]
				src_width = full_image.shape[1]
				dst_height = m.array[:, :, 0].shape[0]
				dst_width = m.array[:, :, 0].shape[1]
				#display_image = cv2.resize(display_image, dsize=(dst_width, dst_height), interpolation=cv2.INTER_CUBIC)

				m.array[:, :, 0] = m.array[:, :, 1] = m.array[:, :, 2] = display_image

				full_image = None
				display_image = None

			if self.zebras:
				zebra_b = cv2.compare(m.array[:, :, 0], 254, cv2.CMP_GE)
				zebra_g = cv2.compare(m.array[:, :, 1], 254, cv2.CMP_GE)
				zebra_r = cv2.compare(m.array[:, :, 2], 254, cv2.CMP_GE)
				zebra_all = cv2.bitwise_or(zebra_b, zebra_g)
				zebra_all = cv2.bitwise_or(zebra_all, zebra_r)

			# Takes about 0.39s, so only auto stretch when taking photos
			if (self.operatingMode == OperatingMode.PHOTO or self.operatingMode == OperatingMode.POLAR_ALIGN or self.operatingMode == OperatingMode.OTE_VIDEO) and self.autostretch: 
				#start = time.time()

				#print('Min:', np.min(m.array[:, :, 0]))
				#print('Max:', np.max(m.array[:, :, 0]))

				# Just use one channel (as it's mono), convert to float, scale and conver back
				if self.operatingMode == OperatingMode.OTE_VIDEO:
					(height, width, _)  = m.array.shape
					centerHeight = int(height/2)
					centerWidth = int(width/2)
					pixelWidth = 100
					regionDimensions = (centerHeight - pixelWidth, centerHeight + pixelWidth, centerWidth - pixelWidth, centerWidth + pixelWidth)	# Y1, Y2, X1, X2
					mono = m.array[:, :, 0][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]].astype(np.float32)
				else:
					mono = m.array[:, :, 0].astype(np.float32)
				mono -= self.autoStretchLower
				scaling = 255.0 / (self.autoStretchUpper - self.autoStretchLower)
				mono *= scaling

				# Clamp 0-255
				mono = np.clip(mono, 0, 255)
				mono.astype(np.uint8)

				if self.operatingMode == OperatingMode.OTE_VIDEO:
					m.array[:, :, 0][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
					m.array[:, :, 1][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
					m.array[:, :, 2][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
				else:
					m.array[:, :, 0] = mono
					m.array[:, :, 1] = mono
					m.array[:, :, 2] = mono

				#print('Min:', np.min(m.array[:, :, 0]))
				#print('Max:', np.max(m.array[:, :, 0]))

				#elapsed = time.time() - start
				#print('Auto-Stretch Took: %f seconds' % elapsed)

			if self.zebras:
				m.array[:, :, 1] = cv2.bitwise_or(zebra_all, m.array[:, :, 1])
				zebra_not_all	 = cv2.bitwise_not(zebra_all)
				m.array[:, :, 0] = cv2.bitwise_and(zebra_not_all, m.array[:, :, 0])
				m.array[:, :, 2] = cv2.bitwise_and(zebra_not_all, m.array[:, :, 2])
				zebra_not_all	 = None
				zebra_all	 = None

			if self.crosshairs:
				(height, width, _)  = m.array.shape
				w2 = int(width/2)
				h2 = int(height/2)
				cv2.line(m.array, (w2, 0), (w2, height-1), (0, 255, 0), 2)
				cv2.line(m.array, (0, h2), (width-1, h2), (0, 255, 0), 2)

			if self.stardetection:
				fwhmAvg = 0.0
				sharpnessAvg = 0.0
				(height, width, _)  = m.array.shape
				if sources is not None:
					for source in sources:
						print(source.keys())
						x = int(float(source['xcentroid']) * float(dst_width) / float(src_width))
						y = int(float(source['ycentroid']) * float(dst_height) / float(src_height))
						fwhmAvg += source['fwhm']
						sharpnessAvg += source['sharpness']

						cv2.circle(m.array, (x, y), 10, (0, 255, 0), 1)
						cv2.putText(m.array, '%0.2f' % source['fwhm'], (x+12, y), self.font, self.scale, (0,255,0),  self.thickness)

					fwhmAvg /= float(len(sources))				
					sharpnessAvg /= float(len(sources))				

					cv2.putText(m.array, 'Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (fwhmAvg, sharpnessAvg), (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)
				else:
					cv2.putText(m.array, 'No stars detected', (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)

			cv2.putText(m.array, timestamp, self.origin, self.font, self.scale, self.color, self.thickness)


		sensor_timestamp_delta = (metadata['SensorTimestamp'] - self.last_sensor_timestamp) / 1000
		self.last_sensor_timestamp = metadata['SensorTimestamp']

		frame_timestamp_delta = now.timestamp() - self.last_frame_timestamp
		self.last_frame_timestamp = now.timestamp()

		#print("SensorTimestampDelta: %d  ExposureTime: %d  FrameDuration: %d  FPS:%0.3f Time:%s TimeDelta:%f" % (sensor_timestamp_delta, metadata['ExposureTime'], metadata['FrameDuration'], 1000000 / sensor_timestamp_delta, timestamp, frame_timestamp_delta ))
		#print(metadata)
		#print(frame_timestamp_delta)

		#with MappedArray(request, "raw") as raw:
		#	print(raw.array.shape)	
		#	raw.array.tofile('test.raw')


	# Some of the sensor modes do binning, this returns the bin size

	def __modeBinSize(self, mode):
		size = mode['size']
		crop = mode['crop_limits']
		cropSize = (crop[2], crop[3])

		if size[0] == cropSize[0] and size[1] == cropSize[1]:
			return 1
		else:
			binSize = (cropSize[0] / size[0], cropSize[1] / size[1])
			if binSize[0] != binSize[1]:
				raise ValueError('None symmetical binning for mode: %d' % mode_index)
			return binSize[0]


	# Returns the field of view percentage in relation to the full
	# sensor frame size
	# (100.0, 100.0) 	= Full Frame
	# (50.00, 75.00)	= 50% of Width and 75% of Height of the full frame

	def __modeFieldOfViewPercentage(self, mode):
		crop = mode['crop_limits']
		cropSize = (crop[2], crop[3])
		return (cropSize[0] * 100.0 / self.full_frame_size[0], cropSize[1] * 100.0 / self.full_frame_size[1])


	# Returns the selected cameraMode

	def __cameraSelectedMode(self):
		return self.sensor_modes[self.settings['mode_selected']]


	def __startVideoRecording(self):
		if self.operatingSubMode != OperatingVideoMode.PREVIEW:
			raise ValueError('OperatingVideoMode != PREVIEW')

		print("Start Video Recording")

		if self.ui.videoFrameRateWarning():
			self.ui.panelTask.widgetRecord.setChecked(False)
			return

		video_filename = self.settings['videoFolder'] + '/' + self.videoTarget  + datetime.utcnow().strftime('_%Y%m%d_%H%M%S') + '.ravf'

		# No longer possible, each video_filename is unique because of the timestamp
		#if os.path.exists(video_filename):
		#	self.ui.messageBoxVideoFileOverwriteQuestion(video_filename)
		#	self.ui.panelTask.widgetRecord.setChecked(False)
		#	return
		print(video_filename)

		self.ui.indeterminateProgressBar(True)

		self.ui.panelTask.setEnabledUi(False)

		self.picam2.stop()
		#GOOD encoder = AdvEncoder(bits_per_pixel=16, native_bits_per_pixel=16, data_layout=SimpleAdv2DataLayout.IMAGE_FULL_RAW, clock_frequency=1000000, clock_accuracy=1, timestamp_absolute_accuracy_ns=1000, compression=SimpleAdv2Compression.UNCOMPRESSED, regions_of_interest=None)
		#GOOD encoder = AdvEncoder(bits_per_pixel=16, native_bits_per_pixel=12, data_layout=SimpleAdv2DataLayout.IMAGE_FULL_RAW, clock_frequency=1000000, clock_accuracy=1, timestamp_absolute_accuracy_ns=1000, compression=SimpleAdv2Compression.UNCOMPRESSED, regions_of_interest=None)

		image_format = self.picam2_video_config['raw']['format']
		if image_format == 'SBGGR10_CSI2P':
		     ravf_image_format	= RavfImageFormat.FORMAT_PACKED_10BIT
		     ravf_color_type	= RavfColorType.BAYER_BGGR
		elif image_format == 'R10_CSI2P':
		     ravf_image_format	= RavfImageFormat.FORMAT_PACKED_10BIT
		     ravf_color_type	= RavfColorType.MONO
		elif image_format == 'SBGGR12_CSI2P':
		     ravf_image_format	= RavfImageFormat.FORMAT_PACKED_12BIT
		     ravf_color_type	= RavfColorType.BAYER_BGGR
		elif image_format == 'SBGGR10':
		     ravf_image_format	= RavfImageFormat.FORMAT_UNPACKED_10BIT
		     ravf_color_type	= RavfColorType.BAYER_BGGR
		elif image_format == 'SBGGR12':
		     ravf_image_format	= RavfImageFormat.FORMAT_UNPACKED_12BIT
		     ravf_color_type	= RavfColorType.BAYER_BGGR
		else:
		    raise ValueError('Unrecognized image format: %s' % image_format)
               
		if self.objectCoords is None:
			(ra, dec) = (float(0.0), float(0.0))
		else:
			(ra, dec) = self.objectCoords.raDec360Deg('icrs')
			ra = float(ra)
			dec = float(dec)
			
		mode = self.__cameraSelectedMode()
		bining = self.__modeBinSize(mode)
		bining = (bining, bining)
		objName = self.ui.panelObject.widgetSearch.text()

		video_logfile = video_filename.replace('.ravf', '.log')
		self.logger.info('switching logging to: %s' % video_logfile)
		self.processLogger.queue.put( { 'cmd': 'change_file', 'fname': video_logfile } )
		self.processLogger.setPropagate(False)	# Otherwise a default logger outputs subprocess logging information

		encoder = RavfEncoder(filename = video_filename, image_format = ravf_image_format, color_type = ravf_color_type, ra = ra, dec = dec, binning = bining, objName = objName, shutter_ns = self.picam2_video_config['controls']['ExposureTime'] * 1000, sensor = self.picam2.camera_properties['Model'], frameDuration = self.videoFrameDuration, camera = self)

		self.picam2.start_recording(encoder, None)
		self.operatingSubMode = OperatingVideoMode.RECORDING


	def __stopVideoRecording(self):
		if self.operatingSubMode != OperatingVideoMode.RECORDING:
			raise ValueError('OperatingVideoMode != RECORDING')

		print("**** Stopping Video Recording")
		self.picam2.stop_recording()
		print("**** picam2 hard stop")
		self.picam2.stop_()
		time.sleep(1)
		self.operatingSubMode = OperatingVideoMode.PREVIEW
		self.ui.panelTask.widgetRecord.setChecked(False)
		self.ui.panelTask.setEnabledUi(True)
		self.ui.indeterminateProgressBar(False)

		if self.settings['prompt_dark_after_acquisition'] and not self.plannedAutoShutdown:
			self.ui.messageBoxTakeDark()
		

	def __capture_file_or_array(self, file_output, obsDateTime, name: str, format=None) -> dict:
		request = self.picam2.completed_requests.pop(0)

		metadata = request.get_metadata()

		arr = None

		if file_output == None:
			arr = request.make_array(name)
			mode = self.__cameraSelectedMode()
			modeExtra = { 'bining': self.__modeBinSize(mode), 'pixelSize':(self.picam2.camera_properties['UnitCellSize'][0]/1000.0,self.picam2.camera_properties['UnitCellSize'][1]/1000.0), 'model': self.picam2.camera_properties['Model'] }
			self.lastFitFile = self.fileHandling.save_photo_fit(arr, metadata, self.__cameraSelectedMode(), modeExtra, obsDateTime, Settings.getInstance().platesolver['focal_length'], self.lastMountCoords)
		else:
			print("Name:", name)
			if name == "raw" and formats.is_raw(self.picam2.camera_config["raw"]["format"]):
				self.fileHandling.save_photo_dng(request, metadata)
			#else:
			#	request.save(name, file_output, format=format)

		request.release()

		return (True, metadata, arr)


	# This stops the preview automatically starting up again after taking a photo
	# Ammended from: Reference: PiCamera2 manual

	def __take_photo(self, camera_config, file_output, name="main", wait="True", signal_function=None):
		def capture_and_stop_(file_output, obsDateTime):
			res = self.__capture_file_or_array(file_output, obsDateTime, name)
			self.__photoFinishedMetadata(res[1])
			if res[2] is None:
				print("Array is None")
			else:
				print("Array:", res[2].shape)
			self.picam2.stop()
			return (True, None)

		obsDateTime = datetime.utcnow()
		functions = [(lambda: capture_and_stop_(file_output, obsDateTime))]
		return self.picam2.dispatch_functions(functions, wait=wait, signal_function=signal_function)


	def __photoFinishedUi(self, job):
		print("Photo Finished:", job)
		try:
			self.ui.panelTask.widgetRecord.setChecked(False)
			self.ui.panelTask.setEnabledUi(True)
			self.polarAlignUpdateNextButton()
		except Exception as e:
			print("Failed:", e)
			pass

		if self.operatingMode == OperatingMode.PHOTO:
			self.operatingSubMode = OperatingPhotoMode.IDLE
			self.photoCountCurrent = self.photoCountCurrent - 1
			if self.photoCountCurrent > 0:
				print("Taking another photo:", self.photoCountCurrent)
				self.ui.panelTask.widgetNumSubs.setText(str(self.photoCountCurrent))
				self.photoCountTotal = 1
				self.ui.panelTask.widgetRecord.setChecked(True)
				self.ui.panelTask.setEnabledUi(False)
				if self.dithering:
					self.dither()
				self.__startPhoto()
			else:
				self.ui.indeterminateProgressBar(False)
		elif self.operatingMode == OperatingMode.POLAR_ALIGN:
			self.operatingSubMode = OperatingPhotoMode.IDLE
			self.photoCountCurrent = self.photoCountCurrent - 1
			self.ui.indeterminateProgressBar(False)
		elif self.operatingMode == OperatingMode.OTE_VIDEO or self.operatingMode == OperatingMode.VIDEO:
			print('Workaround to previous photo cancel...  Cancelling a photo then switching to video mode ends up with video not starting because of a pending photo finished.  This fixes that by stopping and starting the camera to reset it.')
			self.picam2.stop()
			time.sleep(1)
			self.picam2.start()

		if self.photoCallback is not None:
			self.photoCallback()


	def __photoFinishedMetadata(self, metadata):
		print("Metadata:", metadata)


	def __startPhoto(self):
		self.logger.debug('Photo Started')
		if self.operatingSubMode != OperatingPhotoMode.IDLE:
			raise ValueError('OperatingPhotoMode != IDLE')
	
		print("Start Photo Recording")

		self.ui.indeterminateProgressBar(True)
		self.operatingSubMode = OperatingPhotoMode.RECORDING_SINGLE

		if self.settings['photo_format'] == 'fit':
			file_output = None
		else:
			file_output = 'test_full'

		self.lastSolvedPosition = None
		
		self.ui.panelTask.setEnabledUi(False)
		self.picam2.start()
		job = self.__take_photo(self.picam2_still_config, file_output, name="raw", wait=False, signal_function=self.__photoFinishedUi)
		print(job)


	def __cancelPhoto(self):
		if self.operatingSubMode != OperatingPhotoMode.RECORDING_SINGLE:
			raise ValueError('OperatingPhotoMode != RECORDING_SINGLE')

		print("Cancelling Photo Recording")

		# Reference: https://github.com/raspberrypi/picamera2/discussions/589
		self.picam2.stop_()
		time.sleep(1)

		self.photoCountTotal = 1
		self.photoCountCurrent = 1
		self.ui.panelTask.widgetNumSubs.setText("1")

		self.operatingSubMode = OperatingPhotoMode.IDLE
		self.ui.panelTask.setEnabledUi(True)
		self.ui.panelTask.widgetRecord.setChecked(False)
		self.ui.indeterminateProgressBar(False)


	def startRecording(self):
		if   self.operatingMode == OperatingMode.OTE_VIDEO or self.operatingMode == OperatingMode.VIDEO:
			self.__startVideoRecording()
		elif self.operatingMode == OperatingMode.PHOTO or self.operatingMode == OperatingMode.POLAR_ALIGN:
			self.__startPhoto()
			print("Setting photoCountCurrent to:", self.photoCountCurrent)
			self.photoCountCurrent = self.photoCountTotal


	# Stops recording
	def stopRecording(self):
		if   self.operatingMode == OperatingMode.OTE_VIDEO or self.operatingMode == OperatingMode.VIDEO:
			self.__stopVideoRecording()
			self.picam2.start()	
		elif self.operatingMode == OperatingMode.PHOTO or self.operatingMode == OperatingMode.POLAR_ALIGN:
			self.__cancelPhoto()


	def switchMode(self, mode):
		if mode == self.operatingMode:
			return

		# We reset the polar align on any mode change and enable the Next Step Button for Polar Alignment
		self.polarAlignStep	= 0
		self.polarAlignTestIndex= 3
		self.polarAlignUpdateNextButton()

		# Shutdown up any recording operations first before we change modes
		# and any other things we need to shutdown
		currentMode = self.operatingMode
		if   currentMode == OperatingMode.PHOTO or currentMode == OperatingMode.POLAR_ALIGN:
			if self.operatingSubMode == OperatingPhotoMode.RECORDING_SINGLE or self.operatingSubMode == OperatingPhotoMode.RECORDING_SEQUENCE:
				self.__cancelPhoto()
		elif currentMode == OperatingMode.OTE_VIDEO or currentMode == OperatingMode.VIDEO:
			if self.operatingSubMode == OperatingVideoMode.RECORDING:
				self.__stopVideoRecording()

			# Abruptly shutdown the preview such that we loose any queued frames too
			self.picam2.stop_()
			time.sleep(1)
		else:
			raise ValueError('Unrecognized operatingMode')

		# Setup the new mode and start what needs to be started
		self.operatingMode = mode

		if self.operatingMode == OperatingMode.POLAR_ALIGN:
			self.ui.panelObject.setEnabledUi(False)
		else:
			self.statusMsg('')
			self.ui.panelObject.setEnabledUi(True)

		if   self.operatingMode == OperatingMode.OTE_VIDEO or self.operatingMode == OperatingMode.VIDEO:
			self.lastSolvedPosition = None
			self.operatingSubMode = OperatingVideoMode.PREVIEW
			self.picam2.configure(self.picam2_video_config)
			self.picam2.start()
		elif self.operatingMode == OperatingMode.PHOTO or self.operatingMode == OperatingMode.POLAR_ALIGN:
			self.operatingSubMode = OperatingPhotoMode.IDLE
			self.picam2.configure(self.picam2_still_config)
			if self.operatingMode == OperatingMode.POLAR_ALIGN:
				self.statusMsgPolarAlign('')
				if self.settings['polar_align_test']:
					self.ui.messageBoxPolarAlignTestModeWarning()
				
		if self.operatingMode == OperatingMode.POLAR_ALIGN:
			randomString		= ''.join(random.choices(string.ascii_lowercase, k=5))	# Generate random string of 5 chars for each session
			self.fileHandling	= FileHandling(self.settings['photosFolder'], randomString, FileHandlingImageType.PHOTO_POLAR_ALIGN)
			self.ui.panelObject.setVisible(False)
		else:
			self.fileHandling	= self.photoFileHandling
			self.ui.panelObject.setVisible(True)

		print('switchMode:', self.operatingMode)


	def statusMsg(self, msg):
		if self.ui is not None:
			self.ui.showStatusMessage(msg)


	def solveFieldFailed(self):
		#self.plateSolverThread = None	
		print("Plate Solver Failed")
		self.ui.panelTask.updatePlateSolveFailed()
		self.ui.indeterminateProgressBar(False)


	def solveFieldSuccess(self, position, field_size, rotation_angle, index_file, focal_length, altAz):
		self.lastSolvedPosition = position
		self.ui.panelTask.updatePlateSolveSuccess(self.lastSolvedPosition, field_size, rotation_angle, index_file, focal_length, altAz)
		self.ui.indeterminateProgressBar(False)
		if self.platesolveCallback is not None:
			self.platesolveCallback(position, field_size, altAz)


	def solveFieldCancel(self):
		if self.plateSolverThread is not None:
			print('Cancelling plate solver')
			self.plateSolverThread.cancel()
		self.ui.indeterminateProgressBar(False)


	def solveField(self, fname):
		self.ui.indeterminateProgressBar(True)
		self.plateSolverThread = PlateSolver(fname, self.search_full_sky, progress_callback=self.statusMsg, success_callback=self.solveFieldSuccess, failure_callback=self.solveFieldFailed)


	def polarAlignCallback(self, solveSuccess, position, delta=None):
		if solveSuccess:
			if self.polarAlignStep >= 6:
				self.polarAlignStep = 5
			else:
				self.polarAlignStep += 1
			if position is not None:
				self.lastSolvedPosition = position
				if delta is not None and Settings.getInstance().platesolver['direction_indicator_polar_align'] != 'None':
					self.ui.panelTask.launchPolarAlignDirectionDialog(delta)
		else:
			self.polarAlignStep -= 1
			self.lastSolvedPosition = None

		self.paSolver = None
		self.ui.indeterminateProgressBar(False)

		print("Next Polar Align Step:", self.polarAlignStep)
		self.polarAlignUpdateNextButton()


	def polarAlignCancel(self):
		print('Polar Align Cancel:', self.polarAlignStep)
		if self.paSolver is not None:
			print('Cancelling plate solver')
			self.paSolver.cancel()

		if self.operatingSubMode == OperatingPhotoMode.RECORDING_SINGLE:
			self.__cancelPhoto()
			self.polarAlignStep -= 1

		if self.trackingActivatedNotify:
			print('Cancel Rotation')
			self.indi.telescope.abortMotion()
			self.polarAlignStep = 0
			self.polarAlignTestIndex= 3
			self.trackingActivatedNotify = False

		self.ui.indeterminateProgressBar(False)

		self.polarAlignUpdateNextButton()
		self.statusMsgPolarAlign('')

		print('New Polar ALign Step', self.polarAlignStep)


	def polarAlignTrackingActivated(self):
		print('Tracking activated, rotation complete')
		self.trackingActivatedNotify = False
		self.pa.step2(self.polarAlignCallback)


	def statusMsgPolarAlign(self, msg):
		if   self.polarAlignStep == 0:
			stepTxt = 'PA Step 0 (Site set, ** Set mount to Home position before proceeding **. Take Photo A)'
		elif self.polarAlignStep == 1:
			stepTxt = 'PA Step 1 (Plate Solve Photo A)'
		elif self.polarAlignStep == 2:
			stepTxt = 'PA Step 2 (Rotate RA +/-%0.1fdeg)' % self.settings['polar_align_rotation']
		elif self.polarAlignStep == 3:
			stepTxt = 'PA Step 3 (Take Photo B)'
		elif self.polarAlignStep == 4:
			stepTxt = 'PA Step 4 (Plate Solve Photo B)'
		elif self.polarAlignStep == 5:
			stepTxt = 'PA Step 5 (Take Photo I)'
		elif self.polarAlignStep == 6:
			stepTxt = 'PA Step 6 (Plate Solve Photo I)'
			
		self.statusMsg("%s: %s" % (stepTxt,msg) )


	def polarAlignUpdateNextButton(self):
		if   self.polarAlignStep == 0:
			nextButtonTxt = 'Next - Take Photo A'
		elif self.polarAlignStep == 1:
			nextButtonTxt = 'Next - Plate Solve Photo A'
		elif self.polarAlignStep == 2:
			nextButtonTxt = 'Next - Rotate RA +/-%0.1fdeg' % self.settings['polar_align_rotation']
		elif self.polarAlignStep == 3:
			nextButtonTxt = 'Next - Take Photo B'
		elif self.polarAlignStep == 4:
			nextButtonTxt = 'Next - Plate Solve Photo B'
		elif self.polarAlignStep == 5:
			nextButtonTxt = 'Next - Take Photo I'
		elif self.polarAlignStep == 6:
			nextButtonTxt = 'Next - Plate Solve Photo I'
			
		self.ui.panelTask.widgetPANext.setText(nextButtonTxt)


	def polarAlign(self):
		testMode = self.settings['polar_align_test']
	
		self.statusMsgPolarAlign('')

		if   self.polarAlignStep == 0:
			self.indi.telescope.tracking(False)
			self.pa = PolarAlign(self.statusMsgPolarAlign)
			self.fileHandling.setPrepend('A')
			self.startRecording()
			self.polarAlignStep += 1
		elif self.polarAlignStep == 1:
			if testMode:
				self.lastFitFile = pa_test_images_folder + 'PA_0001.fit'
			self.ui.indeterminateProgressBar(True)
			self.paSolver = self.pa.step1(self.lastFitFile, self.search_full_sky, self.polarAlignCallback)
		elif self.polarAlignStep == 2:
			# Rotate the mount in RA
			self.ui.indeterminateProgressBar(True)
			(ra, dec) = self.lastMountCoords.raDec24Deg('icrs')	# Really in Mount Format(JNOW or J2000) not ICRS
			raRotated = ra + ((self.settings['polar_align_rotation'] / 360.0) * 24.0)
			if raRotated >= 24.0:
				raRotated = raRotated - 24.0
			mountPositionRotated = AstCoord.from24Deg(raRotated, dec, 'icrs')	# Really in JNOW not ICRS
			print("Rotated:", mountPositionRotated)
			self.lastSolvedPosition = None
			self.trackingActivatedNotify = True
			if self.mountCanMove():
				self.indi.telescope.goto(mountPositionRotated, already_in_mount_native=True)
		elif self.polarAlignStep == 3:
			self.fileHandling.setPrepend('B')
			self.startRecording()
			self.polarAlignStep += 1
		elif self.polarAlignStep == 4:
			if testMode:
				self.lastFitFile = pa_test_images_folder + 'PA_0002.fit'
			self.ui.indeterminateProgressBar(True)
			self.paSolver = self.pa.step3(self.lastFitFile, self.search_full_sky, self.polarAlignCallback)
		elif self.polarAlignStep == 5:
			self.fileHandling.setPrepend('I')
			self.startRecording()
			self.polarAlignStep += 1
		elif self.polarAlignStep == 6:
			if testMode:
				self.lastFitFile = pa_test_images_folder + 'PA_00%02d.fit' % self.polarAlignTestIndex
				if self.polarAlignTestIndex < 7:
					self.polarAlignTestIndex += 1

			self.ui.indeterminateProgressBar(True)
			self.paSolver = self.pa.step4(self.lastFitFile, self.search_full_sky, self.polarAlignCallback)


	def updateRaDecPos(self, coord):
		self.lastMountCoords = coord	# Really in Mount Format(JNOW or J2000) not ICRS
		if self.ui:
			#print("Mount update position:", self.lastMountCoords.raDec24Deg('icrs'))
			self.ui.panelMount.setRaDecPos(self.lastMountCoords)


	def updateMountPositionDisplay(self):
		self.ui.panelMount.setRaDecPos(self.lastMountCoords)	# Really in Mount Format(JNOW or J2000) not ICRS


	def updateTracking(self, tracking):
		print("Tracking:", tracking)
		if  self.ui is not None and Settings.getInstance().mount['tracking_capable'] and self.ui.panelMount.widgetTracking is not None:
			self.ui.panelMount.widgetTracking.setChecked(True if tracking == 1 else False)

			if self.trackingActivatedNotify:
				self.polarAlignTrackingActivated()


	def updatePark(self, park):
		print("Park:", park)
		if  self.ui is not None and self.ui.panelMount.widgetHome is not None:
			self.ui.panelMount.widgetHome.setChecked(True if park == 1 else False)


	def syncLastPlateSolve(self):
		if self.lastSolvedPosition is not None:
			if self.mountCanMove():
				self.indi.telescope.sync(self.lastSolvedPosition)
		else:
			self.ui.panelMount.messageBoxNoPlateSolve()
			print("No last solved position to sync")


	def setPhotoCountTotal(self, count):
		self.photoCountTotal = count
		print("Photo Count Total Changed To:", count)


	def setJobName(self, object):
		self.photoFileHandling.setTarget(object)	
		self.videoTarget = object
		print("Set Object:", object)


	def searchObject(self, search):
		print("Search Object:", search)

		obj = self.ui.panelObject.findObject(search)

		if obj is not None:
			self.ui.panelObject.setRaDec(obj)


			if self.ui.panelObject.messageBoxSearchObjectSuccess(search, obj):
				self.objectCoords = obj
				self.lastCoords	= self.objectCoords
				self.lastSolvedPosition = None
				self.ui.panelMount.resetUpcomingMeridianFlasher()
				self.meridianFlipUpdate()
				if Settings.getInstance().mount['goto_capable'] and self.mountCanMove():
					self.indi.telescope.goto(self.objectCoords)
		else:
			self.ui.panelObject.setRaDec(None)
			self.objectCoords = None
			self.ui.panelObject.messageBoxSearchObjectFailed()

	def clearObject(self):
		self.ui.panelObject.setRaDec(None)
		self.objectCoords = None
		self.ui.panelObject.widgetSearch.setText('')


	def setObjectCoords(self, coords):
		self.objectCoords = coords
		self.lastCoords	= self.objectCoords
		self.ui.panelObject.setRaDec(coords)


	def gotoObjectRaDec(self):
		if self.objectCoords is None:
			self.ui.messageBoxGotoNoObject()
		else:
			self.ui.panelMount.resetUpcomingMeridianFlasher()
			if self.mountCanMove():
				self.indi.telescope.goto(self.objectCoords)


	def dither(self):
		ditherMax = (self.settings['dither_ra'], self.settings['dither_dec'])
		ditherAdd = (((random.random() * 2.0) - 1.0) * ditherMax[0], ((random.random() * 2.0) - 1.0) * ditherMax[1])

		(ra, dec) = self.objectCoords.raDec360Deg('icrs')
		(ra, dec) = (ra + ditherAdd[0], dec + ditherAdd[1])
		if ra < 0.0:
			ra = ra + 360.0
		elif ra >= 360.0:
			ra = ra - 360.0
		
		ditheredCoords = AstCoord.from360Deg(ra, dec, 'icrs')
		print("Ditherered:", ditheredCoords)
		self.lastCoords = ditheredCoords
		if self.mountCanMove():
			self.indi.telescope.goto(ditheredCoords)
		time.sleep(2)


	def setDither(self, enable):
		print("Dithering set to:", enable)
		self.dithering = enable


	def toggleTracking(self):
		print("Toggle Tracking")
		if self.indi.telescope.getTracking():
			self.indi.telescope.tracking(False)
		else:
			self.indi.telescope.tracking(True)


	def setAutoStretch(self, enable):
		self.autostretch = enable


	def meridianFlipUpdate(self):
		if Settings.getInstance().mount['align_axis'] == 'eq' and self.objectCoords is not None:
			meridianFlipInMins = self.objectCoords.meridianFlipMins()
			print("Meridian Flip In %d mins" % int(meridianFlipInMins))
			self.ui.panelMount.setMeridian(meridianFlipInMins)

	def setZebras(self, enable):
		self.zebras = enable

	def shutdown(self):
		self.indi.disconnect()
		self.picam2.close()

	def setFullSkySolve(self, enable):
		self.search_full_sky = enable

	def togglePark(self):
		if self.indi.telescope.getPark():
			self.indi.telescope.park(False)
		else:
			self.indi.telescope.park(True)

	def exitNow(self):
		print('Exiting now...')
		raise RuntimeError('CameraModel Exit: This is not an error')

	def nextUsbTty(self):
		lastNumber = int(self.indi_usb_tty[-1])
		lastNumber += 1
		self.indi_usb_tty = self.indi_usb_tty[:-1] + str(lastNumber)

	def setAutoStretchLimits(self, lower: float, upper: float):
		self.autoStretchLower = lower
		self.autoStretchUpper = upper


	def setCrossHairs(self, enable):
		self.crosshairs = enable


	def setStarDetection(self, enable):
		self.stardetection = enable


	def simulateMount(self):
		self.simulate = True


	# Returns True if the mount can move/sync otherwise false
	# Prompts the user to unpark the mount if parked
	# if isParkedReturnFalse=True, return True if user chooses to unpark the scope
	# otherwise False

	def mountCanMove(self, isParkedReturnFalse=False):
		if self.indi.telescope.getPark():
			ret = QMessageBox.question(self.ui, ' ', "Mount is PARKED, do you wish to unpark it?", QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.Yes:
				self.indi.telescope.park(False)
				time.sleep(1)
				if isParkedReturnFalse:
					return False
				return True
			else:
				return False
		return True


	def setGain(self, gain: float):
		print('setGain')
		#'AnalogueGain':		self.settings['gain'],
		self.picam2_still_config['controls']['AnalogueGain'] = gain
		self.picam2_video_config['controls']['AnalogueGain'] = gain

		# Update the live config
		self.picam2.controls.AnalogueGain = gain

		Settings.getInstance().camera['gain'] = gain
		Settings.getInstance().writeSubsetting('camera')


	def takePhotoSolveSync(self, dialog):
		self.photoCallback = self.takePhotoSolveSync2
		self.dialogPrepoint = dialog
		self.startRecording()

	
	def takePhotoSolveSync2(self):
		self.photoCallback = None

		if self.settings['polar_align_test']:
			self.ui.messageBoxPrepointTestModeWarning()
			fname = '/media/pi/ASTRID/TestPlateSolveImages/midi80-qhy5Lii-FR.fit'
		else:
			fname = self.lastFitFile

		self.platesolveCallback = self.takePhotoSolveSync3
		self.solveField(fname)


	def takePhotoSolveSync3(self, position, field_size, altAz):
		self.platesolveCallback = None
		print('Syncing solved position:', position.raDecHMSStr('icrs'))
		self.syncLastPlateSolve()
		self.dialogPrepoint.photoProcComplete(position, field_size, altAz)


	def gotoNoTracking(self, coords):
		self.indi.telescope.tracking(False)
		self.ui.panelMount.resetUpcomingMeridianFlasher()
		if self.mountCanMove():
			self.indi.telescope.goto(coords, no_tracking = True)

	def isPhotoMode(self):
		if self.operatingMode == OperatingMode.PHOTO:
			return True
		return False


	def isOTEVideoMode(self):
		if self.operatingMode == OperatingMode.OTE_VIDEO:
			return True
		return False


	def setPlannedAutoShutdown(self, enable):
		self.plannedAutoShutdown = enable

	
	def isVideoRecording(self):
		return True if self.operatingSubMode == OperatingVideoMode.RECORDING else False
