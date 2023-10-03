import cv2
import numpy as np
from astropy.stats import sigma_clipped_stats
#from photutils.detection import DAOStarFinder
from photutils.detection import IRAFStarFinder


class DisplayOps():

	def __init__(self):
		pass


	def __analyze_stardetection(self, image_buffer):
		#full_image = fits.getdata(Settings.getInstance().astrid_drive + '/Photo/Light/None_0209.fit', ext = 0)
		full_image = image_buffer.array[:, :, 0]
			
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
		dst_height = image_buffer.array[:, :, 0].shape[0]
		dst_width = image_buffer.array[:, :, 0].shape[1]
		#display_image = cv2.resize(display_image, dsize=(dst_width, dst_height), interpolation=cv2.INTER_CUBIC)

		image_buffer.array[:, :, 0] = image_buffer.array[:, :, 1] = image_buffer.array[:, :, 2] = display_image

		full_image = None
		display_image = None


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
		fwhmAvg = 0.0
		sharpnessAvg = 0.0
		(height, width, _)  = image_buffer.array.shape
		if sources is None:
			cv2.putText(image_buffer.array, 'No stars detected', (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)
		else:
			for source in sources:
				print(source.keys())
				x = int(float(source['xcentroid']) * float(dst_width) / float(src_width))
				y = int(float(source['ycentroid']) * float(dst_height) / float(src_height))
				fwhmAvg += source['fwhm']
				sharpnessAvg += source['sharpness']

				cv2.circle(image_buffer.array, (x, y), 10, (0, 255, 0), 1)
				cv2.putText(image_buffer.array, '%0.2f' % source['fwhm'], (x+12, y), self.font, self.scale, (0,255,0),  self.thickness)

			fwhmAvg /= float(len(sources))				
			sharpnessAvg /= float(len(sources))				

			cv2.putText(image_buffer.array, 'Avg FWHM: %0.2f, Avg Sharpness: %0.2f' % (fwhmAvg, sharpnessAvg), (20, height - 40), self.font, self.scale, (0, 255, 0), self.thickness)


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
