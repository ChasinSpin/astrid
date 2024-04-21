import cv2
import math
import numpy as np
from astropy.io import fits
from settings import Settings
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
		self.font	= cv2.FONT_HERSHEY_PLAIN
		self.scale	= 1.0
		self.thickness	= 1


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

		if stretch[0] < stretch[1]:
			mono -= stretch[0]
		else:
			mono -= stretch[1]
		stretchDelta = stretch[1] - stretch[0]
		if stretchDelta < 0:
			stretchDelta = -stretchDelta
		elif stretchDelta == 0:
			stretchDelta = 1
		scaling = 255.0 / stretchDelta
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
		general = Settings.getInstance().general
		if general['center_marker'] == 'crosshairs':
			(height, width, _)  = image_buffer.array.shape
			w2 = int(width/2)
			h2 = int(height/2)
			cv2.line(image_buffer.array, (w2, 0), (w2, height-1), (0, 255, 0), 1)
			cv2.line(image_buffer.array, (0, h2), (width-1, h2), (0, 255, 0), 1)
		elif general['center_marker'] == 'rectangle':
			boxSize = 15
			(height, width, _)  = image_buffer.array.shape
			w2 = int(width/2)
			h2 = int(height/2)
			fromPoint = (w2-boxSize, h2-boxSize)
			toPoint = (w2+boxSize, h2+boxSize)
			cv2.rectangle(image_buffer.array, fromPoint, toPoint, (0, 255, 0), 1)
		elif general['center_marker'] == 'small cross':
			lineGap = 10
			lineLength = 30
			(height, width, _)  = image_buffer.array.shape
			w2 = int(width/2)
			h2 = int(height/2)
			cv2.line(image_buffer.array, (w2, h2-lineGap), (w2, h2-lineLength), (0, 255, 0), 1)
			cv2.line(image_buffer.array, (w2, h2+lineGap), (w2, h2+lineLength), (0, 255, 0), 1)
			cv2.line(image_buffer.array, (w2-lineGap, h2), (w2-lineLength, h2), (0, 255, 0), 1)
			cv2.line(image_buffer.array, (w2+lineGap, h2), (w2+lineLength, h2), (0, 255, 0), 1)


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

				cv2.circle(image_buffer.array, (x, y), 10, (0, 255, 0), 1, cv2.LINE_AA)
				cv2.putText(image_buffer.array, '%0.2f' % hfd, (x+12, y+6), self.font, self.scale, (0,255,0),  self.thickness)

			fwhmAvg /= float(len(self.sources))				
			hfdAvg /= float(len(self.sources))				
			sharpnessAvg /= float(len(self.sources))				

			#cv2.putText(image_buffer.array, 'Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (fwhmAvg, sharpnessAvg), (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)
			self.camera.statusMsg('Avg HFD: %0.2f, Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (hfdAvg, fwhmAvg, sharpnessAvg))

		self.calib_img = None


	def __display_annotation(self, image_buffer, annotationStars):
		src_height = 1088
		src_width = 1456
		dst_height = image_buffer.array[:, :, 0].shape[0]
		dst_width = image_buffer.array[:, :, 0].shape[1]
		print('src: %d %d' % (src_height, src_width))
		print('dst: %d %d' % (dst_height, dst_width))
		for star in annotationStars:
			x = int(star.xy[0] * float(dst_width) / float(src_width))
			y = int(star.xy[1] * float(dst_height) / float(src_height))
			cv2.circle(image_buffer.array, (x, y), 7, (0, 255, 0), 1, cv2.LINE_AA)
			cv2.putText(image_buffer.array, '%0.2f' % star.mag_g, (x-5, y-7), self.font, self.scale, (0,255,0),  self.thickness)


	def __display_object_target(self, image_buffer, pos, targetOutsideImage):
		centerGap = 10
		lineLength = 30
		lineThickness = 1
		colors = [(0, 0, 0), (255, 0, 0) if targetOutsideImage else (0, 255, 0)]

		x = pos[0]
		y = pos[1]

		img = image_buffer.array

		for colorThickness in [[colors[0], lineThickness*3], [colors[1], lineThickness]]:
			color           = colorThickness[0]
			thickness       = colorThickness[1]

			cv2.line(img, (x, y-centerGap), (x, y-lineLength), (color), thickness)
			cv2.line(img, (x, y+centerGap), (x, y+lineLength), (color), thickness)
			cv2.line(img, (x-centerGap, y), (x-lineLength, y), (color), thickness)
			cv2.line(img, (x+centerGap, y), (x+lineLength, y), (color), thickness)


	def __analyze_display_image_buffer(self, image_buffer, video_frame_rate, stretch, zebras, crosshairs, stardetection, annotationStars, targetPixelPosition, targetOutsideImage):
		#print('***** ADIB MAX:', np.max(image_buffer.array))
		#print('***** ADIB MIN:', np.min(image_buffer.array))
		#print('***** ADIB DTYPE:', image_buffer.array.dtype)
		#print('***** ADIB SHAPE:', image_buffer.array.shape)
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
		if annotationStars is not None:
			self.__display_annotation(image_buffer, annotationStars)
		if targetPixelPosition is not None:
			self.__display_object_target(image_buffer, targetPixelPosition, targetOutsideImage)


	def overlayDisplayOnImageBuffer(self, image_buffer, video_recording, video_frame_rate, stretch, zebras, crosshairs, stardetection, annotationStars):
		"""
		Overlay Display On The image_buffer (it alters the image_buffer)
	
		image_buffer		= Picam2 Mapped Buffer	
		video_frame_rate	= the frame rate, or None if it's not video
		stretch			= (stretch_lower, stretch_upper) or None if there's no stretch required
		zebras			= True or False
		crosshairs		= True or False
		stardetection		= True or False
		annotationStars		= List of stars
		"""

		if video_frame_rate is not None and video_recording:	# Some operations are too slow for video, disable them
			stardetection	= False
			zebras		= False		

		self.__analyze_display_image_buffer(image_buffer, video_frame_rate, stretch, zebras, crosshairs, stardetection, annotationStars, None, False)


	def __pointOnRect(self, x, y, minX, minY, maxX, maxY):
		"""
			for a point (x, y) outside a rectangle denoted by minX/Y/maxX/Y, returns the intersection point 
			Reference: https://stackoverflow.com/questions/1585525/how-to-find-the-intersection-point-between-a-line-and-a-rectangle
		"""
		midX = (minX + maxX) / 2
		midY = (minY + maxY) / 2
		m = (midY - y) / (midX - x)

		if x <= midX:
			# check "left" side
			minXy = m * (minX - x) + y
			if minY <= minXy and minXy <= maxY:
				return (minX, minXy)

		if x >= midX:
			# check "right" side
			maxXy = m * (maxX - x) + y
			if minY <= maxXy and maxXy <= maxY:
				return (maxX, maxXy)

		if y <= midY:
			# check "top" side
			minYx = (minY - y) / m + x
			if minX <= minYx and minYx <= maxX:
				return (minYx, minY)

		if y >= midY:
			# check "bottom" side
			maxYx = (maxY - y) / m + x
			if minX <= maxYx and maxYx <= maxX:
				return (maxYx, maxY)

		return (x, y)	# Should never happen


	def loadFitsPhotoWithOverlay(self, fits_filename, width, height, stretch, zebras, crosshairs, stardetection, annotationStars, targetPixelPosition):
		"""
		Load fits, adds the overlays and returns the new buffer suitable for use as an overlay
	
		image_buffer		= Picam2 Mapped Buffer	
		video_frame_rate	= the frame rate, or None if it's not video
		stretch			= (stretch_lower, stretch_upper) or None if there's no stretch required
		zebras			= True or False
		crosshairs		= True or False
		stardetection		= True or False
		annotationStars		= List of stars
		targetPixelPosition	= Position of target in pixels on the original fits image, None if no target
		"""

		fits_data = fits.getdata(fits_filename, ext = 0)
		fits_data = fits_data.astype(np.float32)
		#print('***** FITS MAX:', np.max(fits_data))
		#print('***** FITS MIN:', np.min(fits_data))
		fits_data /= 4.0
		fits_data = fits_data.astype(np.uint8)

		targetOutsideImage = False
		if targetPixelPosition is not None:
			# If pixel is outside the image, then bring back inside bounds and identify
			x = targetPixelPosition[0]
			y = targetPixelPosition[1]
			if x < 0 or x >= fits_data.shape[1] or y < 0 or y >= fits_data.shape[0]:
				targetOutsideImage = True
				(x, y) = self.__pointOnRect(x, y, 0, 0, fits_data.shape[1]-1, fits_data.shape[0]-1)

			# Scale the target pixel position to the image size
			targetPixelPosition = (int(x * width/fits_data.shape[1]), int(y * height/fits_data.shape[0]))

		fits_data = cv2.resize(fits_data, (width, height))

		# Image in fits file is never corrected for flipping, but the image we display needs to be corrected for flipping, correct here
		hflip     = Settings.getInstance().camera['hflip']
		vflip     = Settings.getInstance().camera['vflip']

		if hflip or vflip:
			if hflip and vflip:
				flipCode = -1
			elif hflip:
				flipCode = 1
			elif vflip:
				flipCode = 0

			fits_data = cv2.flip(fits_data, flipCode)

		image_buffer = ProxyImageBuffer(np.zeros((height, width, 3), dtype=np.uint8))
		image_buffer.array[:, :, 0]	= fits_data
		image_buffer.array[:, :, 1]	= fits_data
		image_buffer.array[:, :, 2]	= fits_data

		self.__analyze_display_image_buffer(image_buffer, None, stretch, zebras, crosshairs, stardetection, annotationStars, targetPixelPosition, targetOutsideImage)

		image_buffer2 = ProxyImageBuffer(np.zeros((height, width, 4), dtype=np.uint8))
		image_buffer2.array[:, :, 0]	= image_buffer.array[:, :, 0]
		image_buffer2.array[:, :, 1]	= image_buffer.array[:, :, 1]
		image_buffer2.array[:, :, 2]	= image_buffer.array[:, :, 2]
		image_buffer2.array[:, :, 3]	= 255

		image_buffer.array = None
		image_buffer = None

		return image_buffer2
