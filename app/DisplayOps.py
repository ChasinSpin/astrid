import cv2
import math
import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
#from photutils.detection import DAOStarFinder
from photutils.detection import IRAFStarFinder



class ProxyImageBuffer():

	def __init__(self, image_array):
		self.array = image_array



class DisplayOps():

	HFD_OUTER_DIAMETER = 60 

	def __init__(self, camera):
		self.camera	= camera
		self.font	= cv2.FONT_HERSHEY_SIMPLEX
		self.scale	= 1.0
		self.thickness	= 2


	def __insideCircle(self, x, y, centerX, centerY, radius):
		# Returns true if x,y is inside a circle centered at centerX,centerY with radius
		deltaX = x - centerX
		deltaY = y - centerY

		if ((deltaX * deltaX) + (deltaY * deltaY)) <= (radius * radius):
			return True
	
		return False


	def __calcHfd(self, img, outerDiameter: int):
		"""
		Calculates Half Width Diameter.  Reference: https://www.lost-infinity.com/night-sky-image-processing-part-6-measuring-the-half-flux-diameter-hfd-of-a-star-a-simple-c-implementation/
		img = float values

		Expects star centered in the middle of the image (in x and y) and mean background subtracted from image.

		HDF calculation: https://www005.upp.so-net.ne.jp/k_miyash/occ02/halffluxdiameter/halffluxdiameter_en.html
			https://www.cyanogen.com/help/maximdl/Half-Flux.htm

		NOTE: Currently the accuracy is limited by the insideCircle function (-> sub-pixel accuracy).
		NOTE: The HFD is estimated in case there is no flux (HFD ~ sqrt(2) * outerDiameter / 2).
		NOTE: The outer diameter is usually a value which depends on the properties of the optical
		      system and also on the seeing conditions. The HFD value calculated depends on this
		      outer diameter value.
		"""

		width = img.shape[1]
		height = img.shape[0]

		#  Sum up all pixel values in whole circle
		outerRadius = outerDiameter / 2
		sum = 0
		sumDist = 0
		centerX = math.ceil(width / 2.0)
		centerY = math.ceil(height / 2.0)
 
		for y in range(height):
			for x in range(width):
				if self.__insideCircle(x, y, centerX, centerY, outerRadius):
					pixel	= img[y][x]
					sum	+= pixel
					sumDist	+= pixel * math.sqrt(math.pow(x - centerX, 2.0) + math.pow(y - centerY, 2.0))

		# NOTE: Multiplying with 2 is required since actually just the HFR is calculated above
		if sum == 0:	
			return math.sqrt(2.0) * outerRadius
		
		return 2.0 * sumDist/sum


	def __analyze_stardetection(self, image_buffer):
		#full_image = fits.getdata(Settings.getInstance().astrid_drive + '/Photo/Light/None_0209.fit', ext = 0)
		full_image = image_buffer.array[:, :, 0]
			
		bkg_mean, bkg_median, bkg_std = sigma_clipped_stats(full_image, sigma=3.0)
		print((bkg_mean, bkg_median, bkg_std))
		self.calib_img = full_image - bkg_median
		#daofind = DAOStarFinder(fwhm=8.0, threshold=bkg_std * 15.0)
		#self.sources = daofind(self.calib_img)
		iraffind = IRAFStarFinder(threshold=bkg_std * 5.0, fwhm=5.0, exclude_border=True, brightest=40)
		self.sources = iraffind.find_stars(self.calib_img)
		if self.sources is not None and self.sources.colnames is not None:
			for col in self.sources.colnames:
				if col not in ('id', 'npix'):
					self.sources[col].info.format = '%0.2f'	# For consistent table output
			self.sources.pprint(max_width=75)
		
		# Resize to watch screen display size
		self.src_height = full_image.shape[0]
		self.src_width = full_image.shape[1]
		self.dst_height = image_buffer.array[:, :, 0].shape[0]
		self.dst_width = image_buffer.array[:, :, 0].shape[1]

		full_image = None


	def __analyze_zebras(self, image_buffer):
		zebra_b = cv2.compare(image_buffer.array[:, :, 0], 254, cv2.CMP_GE)
		zebra_g = cv2.compare(image_buffer.array[:, :, 1], 254, cv2.CMP_GE)
		zebra_r = cv2.compare(image_buffer.array[:, :, 2], 254, cv2.CMP_GE)
		image_buffer_zebras = cv2.bitwise_or(zebra_b, zebra_g)
		image_buffer_zebras = cv2.bitwise_or(image_buffer_zebras, zebra_r)
		return image_buffer_zebras


	def __display_stretch(self, image_buffer, stretch, video_frame_rate):
		#start = time.time()

		#print('Min:', np.min(image_buffer.array[:, :, 0]))
		#print('Max:', np.max(image_buffer.array[:, :, 0]))

		# Just use one channel (as it's mono), convert to float, scale and convert back

		# If we have frames rates faster than 10fps, then we have to reduce the window to 100 pixels
		reducedStretchWindow = False
		if video_frame_rate is not None and video_frame_rate > 10.0:
			reducedStretchWindow = True
		
		if reducedStretchWindow:
			(height, width, _)  = image_buffer.array.shape
			centerHeight = int(height/2)
			centerWidth = int(width/2)
			pixelWidth = 100
			regionDimensions = (centerHeight - pixelWidth, centerHeight + pixelWidth, centerWidth - pixelWidth, centerWidth + pixelWidth)	# Y1, Y2, X1, X2
			mono = image_buffer.array[:, :, 0][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]].astype(np.float32)
		else:
			mono = image_buffer.array[:, :, 0].astype(np.float32)

		mono -= stretch[0]
		scaling = 255.0 / (stretch[1] - stretch[0])
		mono *= scaling

		# Clamp 0-255
		mono = np.clip(mono, 0, 255)
		mono.astype(np.uint8)

		if reducedStretchWindow:
			image_buffer.array[:, :, 0][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
			image_buffer.array[:, :, 1][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
			image_buffer.array[:, :, 2][regionDimensions[0]:regionDimensions[1], regionDimensions[2]:regionDimensions[3]] = mono
		else:
			image_buffer.array[:, :, 0] = mono
			image_buffer.array[:, :, 1] = mono
			image_buffer.array[:, :, 2] = mono

		#print('Min:', np.min(image_buffer.array[:, :, 0]))
		#print('Max:', np.max(image_buffer.array[:, :, 0]))

		#elapsed = time.time() - start
		#print('Auto-Stretch Took: %f seconds' % elapsed)


	def __display_zebras(self, image_buffer, image_buffer_zebras):
		image_buffer.array[:, :, 1]	= cv2.bitwise_or(image_buffer_zebras, image_buffer.array[:, :, 1])
		image_buffer_zebras_inverse	= cv2.bitwise_not(image_buffer_zebras)
		image_buffer.array[:, :, 0]	= cv2.bitwise_and(image_buffer_zebras_inverse, image_buffer.array[:, :, 0])
		image_buffer.array[:, :, 2]	= cv2.bitwise_and(image_buffer_zebras_inverse, image_buffer.array[:, :, 2])
		image_buffer_zebras_inverse	= None


	def __display_crosshairs(self, image_buffer):
		(height, width, _)  = image_buffer.array.shape
		w2 = int(width/2)
		h2 = int(height/2)
		cv2.line(image_buffer.array, (w2, 0), (w2, height-1), (0, 255, 0), 2)
		cv2.line(image_buffer.array, (0, h2), (width-1, h2), (0, 255, 0), 2)


	def __display_stardetection(self, image_buffer):
		hfdAvg = 0.0
		fwhmAvg = 0.0
		sharpnessAvg = 0.0
		(height, width, _)  = image_buffer.array.shape
		if self.sources is None:
			cv2.putText(image_buffer.array, 'No stars detected', (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)
		else:
			for self.source in self.sources:
				center_x = int(self.source['xcentroid'])
				center_y = int(self.source['ycentroid'])
				radius = 5
				star_img = self.calib_img[center_y-radius:center_y+radius, center_x-radius:center_x+radius]
				star_img = star_img.astype(np.float32)
				hfd = self.__calcHfd(star_img, DisplayOps.HFD_OUTER_DIAMETER)
				print(self.source.keys())
				x = int(float(self.source['xcentroid']) * float(self.dst_width) / float(self.src_width))
				y = int(float(self.source['ycentroid']) * float(self.dst_height) / float(self.src_height))
				hfdAvg += hfd
				fwhmAvg += self.source['fwhm']
				sharpnessAvg += self.source['sharpness']

				cv2.circle(image_buffer.array, (x, y), 10, (0, 255, 0), 1)
				cv2.putText(image_buffer.array, '%0.2f' % hfd, (x+12, y), self.font, self.scale, (0,255,0),  self.thickness)
				#cv2.putText(image_buffer.array, '%0.2f' % self.source['fwhm'], (x+12, y), self.font, self.scale, (0,255,0),  self.thickness)

			fwhmAvg /= float(len(self.sources))				
			hfdAvg /= float(len(self.sources))				
			sharpnessAvg /= float(len(self.sources))				

			#cv2.putText(image_buffer.array, 'Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (fwhmAvg, sharpnessAvg), (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)
			self.camera.statusMsg('Avg HFD: %0.2f, Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (hfdAvg, fwhmAvg, sharpnessAvg))

		self.calib_img = None


	def __analyze_display_image_buffer(self, image_buffer, video_frame_rate, stretch, zebras, crosshairs, stardetection):
		if video_frame_rate is not None and video_frame_rate > 0.5:
			stardetection = False
	
		# First run the operations that need the original data in the image_buffer before it's changed
		if stardetection:
			self.__analyze_stardetection(image_buffer)
		if zebras:
			image_buffer_zebras = self.__analyze_zebras(image_buffer)

		# Next run the operations that change the image_buffer, order is important for thes
		if stretch is not None:
			self.__display_stretch(image_buffer, stretch, video_frame_rate)
		if zebras:
			self.__display_zebras(image_buffer, image_buffer_zebras)
		if crosshairs:
			self.__display_crosshairs(image_buffer)
		if stardetection:
			self.__display_stardetection(image_buffer)


	def overlayDisplayOnImageBuffer(self, image_buffer, video_recording, video_frame_rate, stretch, zebras, crosshairs, stardetection):
		"""
		Overlay Display On The image_buffer (it alters the image_buffer)
	
		image_buffer		= Picam2 Mapped Buffer	
		video_frame_rate	= the frame rate, or None if it's not video
		stretch			= (stretch_lower, stretch_upper) or None if there's no stretch required
		zebras			= True or False
		crosshairs		= True or False
		stardetection		= True or False
		"""

		if video_frame_rate is not None and video_recording:	# Some operations are too slow for video, disable them
			stardetection	= False
			zebras		= False		

		#print('Min:', np.min(image_buffer.array))
		#print('Max:', np.max(image_buffer.array))

		self.__analyze_display_image_buffer(image_buffer, video_frame_rate, stretch, zebras, crosshairs, stardetection)
		


	def loadFitsPhotoWithOverlay(self, fits_filename, width, height, stretch, zebras, crosshairs, stardetection):
		"""
		Load fits, adds the overlays and returns the new buffer suitable for use as an overlay
	
		image_buffer		= Picam2 Mapped Buffer	
		video_frame_rate	= the frame rate, or None if it's not video
		stretch			= (stretch_lower, stretch_upper) or None if there's no stretch required
		zebras			= True or False
		crosshairs		= True or False
		stardetection		= True or False
		"""

		fits_data = fits.getdata(fits_filename, ext = 0)
		fits_data = fits_data.astype(np.float32)
		fits_data /= 4.0
		fits_data = fits_data.astype(np.uint8)

		fits_data = cv2.resize(fits_data, (width, height))

		image_buffer = ProxyImageBuffer(np.zeros((height, width, 3), dtype=np.uint8))
		image_buffer.array[:, :, 0]	= fits_data
		image_buffer.array[:, :, 1]	= fits_data
		image_buffer.array[:, :, 2]	= fits_data

		self.__analyze_display_image_buffer(image_buffer, None, stretch, zebras, crosshairs, stardetection)

		image_buffer2 = ProxyImageBuffer(np.zeros((height, width, 4), dtype=np.uint8))
		image_buffer2.array[:, :, 0]	= image_buffer.array[:, :, 0]
		image_buffer2.array[:, :, 1]	= image_buffer.array[:, :, 1]
		image_buffer2.array[:, :, 2]	= image_buffer.array[:, :, 2]
		image_buffer2.array[:, :, 3]	= 255

		image_buffer.array = None
		image_buffer = None

		return image_buffer2