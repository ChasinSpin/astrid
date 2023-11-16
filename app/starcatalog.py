import math
import struct
import cdshealpix
import astropy.units as u
import numpy as np
from astropy.io import fits
from astropy.wcs import wcs
from astropy.time import Time
from astcoord import AstCoord
from astropy.coordinates import ICRS, FK5, SkyCoord, Distance
from astropy.stats import sigma_clipped_stats
from pyqtree import Index



class Star():

	def __init__(self, source_id, ra, dec, epoch, mag_bp, mag_g, mag_rp, ruwe, flags, diameter, gaia_version, catalog_id, record_num, parallax, pmra, pmdec):
		super().__init__()

		self.source_id		= source_id
		self.ra			= ra			# 360 deg
		self.dec		= dec			# +-90 deg
		self.epoch		= '%0.2f' % epoch		# Year
		self.mag_bp		= mag_bp
		self.mag_g		= mag_g			# Commonly visual magnitude
		self.mag_rp		= mag_rp
		self.ruwe		= ruwe			# Incorrect, investigate
		self.flags		= flags
		self.diameter		= diameter		# mas
		self.gaia_version	= gaia_version
		self.catalog_id		= catalog_id
		self.record_num		= record_num
		self.parallax		= parallax		# mas
		self.pmra		= pmra			# mas/yr
		self.pmdec		= pmdec			# mas/yr
		self.coord		= None


	def epochPropogateToJ2000(self):
		# Propogate the epoch from the epoch the star was measured at to J2000

		# Create a skycoord with self.epoch
		pcoord = SkyCoord(	ra		= self.ra * u.deg,
					dec		= self.dec * u.deg,
					distance	= Distance(parallax = self.parallax * u.mas),
					pm_ra_cosdec	= self.pmra * u.mas/u.yr,
					pm_dec		= self.pmdec * u.mas/u.yr,
					obstime		= Time(self.epoch, format='jyear', scale='tcb')
				)	

		# Create epoch for J2000
		epoch_j2000 = Time('2000.0', format='jyear', scale='tcb')

		# Transform coordinate to the J2000 epoch
		pcoord = pcoord.apply_space_motion(epoch_j2000)

		# Note at this point, it contains the proper motion information
		# e.g.
		#	<SkyCoord (ICRS): (ra, dec, distance) in (deg, deg, pc)
		#   		(2.88360204, 88.38051945, 1230.76923096)
		#	(pm_ra_cosdec, pm_dec, radial_velocity) in (mas / yr, mas / yr, km / s)
		#		(14.15892167, 2.01655003, -9.25708887e-05)>

		# But we're gonna lose this (likely the correct approach) and recreate the object with the ICRS frame
		self.coord = AstCoord.from360Deg(ra = pcoord.ra.value, dec = pcoord.dec.value, frame='icrs')


	def __str__(self):
		return 'gaia_id:%-19d gaia_version:%d catalog_id:%-16s ra:%-13.9f dec:%-12.9f epoch:%s mag_v:%-5.2f ruwe:%-6.3f flags:0x%02X diameter:%-5.3f record_num:%-8d parallax:%f pmra:%f pmdec:%f skyCoord:%s' % \
			(self.source_id, self.gaia_version, self.catalog_id, self.ra, self.dec, self.epoch, self.mag_g, self.ruwe, self.flags, self.diameter, self.record_num, self.parallax, self.pmra, self.pmdec, self.coord)



class StarLookup():

	CATALOGS				= [ {'name': 'gaia', 'fname_data': 'Gaia16_EDR3.bin', 'fname_index': 'Gaia16_EDR3.inx', 'fname_hip_index': 'Hipparcos_Gaia16_EDR3.dat', 'fname_ucac4_index': 'U4_Gaia14.inx', 'fname_tyc_index': 'GSC Fields.dat'} ]
	J2016_J2000_PROPER_MOTION_RADIUS	= 1.8	# The mximum search radius of proper motion between J2016 (Gaia) and J2000(icrs) in Arc Seconds https://www.cosmos.esa.int/web/gaia-users/archive/combine-with-other-data (Cross-Matching Catalogues(Basic))
	debug					= False


	def __init__(self, catalog = 'gaia'):
		"""
			Creates a StarLookup object

			catalog		= 'gaia'
		"""
		super().__init__()

		self.__get_catalog_fnames(catalog)

		if self.fname_data is None or self.fname_index is None:
			raise ValueError('catalog %s not found' % catalog)


	def findStarsInFits(self,  wcsFile: str, magLimit) -> [Star]:
		""""
			Finds stars in the FOV

			Parameters:
				wcsFile	= the .wcs associated with the fits whioch is the result of the plate solve

			Returns:
				list of stars
		"""

		# Read the WCS file to 
		hdulist = fits.open(wcsFile)
		w = wcs.WCS(hdulist[0].header)
		hdulist.close()

		print(w.wcs.name)
		w.wcs.print_contents()
		print(w.wcs.crpix)

		# Derive the image width and height from the center pixel in the WCS
		img_width = int(w.wcs.crpix[0]) * 2
		img_height = int(w.wcs.crpix[1]) * 2
		print('Width:', img_width)
		print('Height:', img_height)
		
		# Visit all 4 corners of the image and determine the RA/DEC of each corner and add to a list of corners
		raCorners = []	
		decCorners = []	
		for corner in [ [0, 0], [0, img_height], [img_width, img_height], [img_width, 0] ]:
			coord = w.pixel_to_world(corner[0], corner[1])
			raCorners.append(coord.ra.value)
			decCorners.append(coord.dec.value)

		# Determine the minimum and maximum RAs and DECs for the search
		raRange = (min(raCorners), max(raCorners))	
		decRange = (min(decCorners), max(decCorners))	

		print('RaRange:', raRange)
		print('DecRange:', decRange)

		# Find all the stars in the raRange / decRange area
		stars = self.findStarsInArea(raRange=raRange, decRange=decRange)
		print('1st pass total stars:', len(stars))


		# Convert the ra/dec of all the stars found back into pixel coordinates in the frame
		worldCoords = np.zeros((len(stars),2), dtype=np.float64)
		for i in range(len(stars)):
			#(ra, dec) = stars[i].coord.raDec360Deg('icrs')
			#worldCoords[i][0] = ra
			#worldCoords[i][1] = dec
			worldCoords[i][0] = stars[i].ra 
			worldCoords[i][1] = stars[i].dec
		pixelCoords = w.wcs_world2pix(worldCoords, 0)

		# Scan the found stars and verifying the xy position is within the frame, building
		# a shorter list of stars (starsInFrame) as we go and setting xy to the position
		starsInFrame = []
		for i in range(len(stars)):
			if pixelCoords[i][0] >= 0 and pixelCoords[i][0] < img_width and \
			   pixelCoords[i][1] >= 0 and pixelCoords[i][1] < img_height and \
			   stars[i].mag_g < magLimit:
				stars[i].xy = (pixelCoords[i][0], pixelCoords[i][1])
				starsInFrame.append(stars[i])

		stars = starsInFrame
		for star in stars:
			print('XY:', star.xy)

		print('2nd pass total stars:', len(stars))
	
		return stars


	def __drawCenterCircle(self, img: np.array, radius: int):
		centerX = img.shape[1] / 2 - 0.5
		centerY = img.shape[0] / 2 - 0.5

		for y in range(img.shape[0]):
			for x in range(img.shape[1]):
				deltaX = x - centerX
				deltaY = y - centerY
				dist = math.sqrt(deltaX * deltaX + deltaY * deltaY)
				if dist <= radius:
					img[y][x] = 1


	def calculateStarMetricsForFits(self,  fitsFile: str, stars: [Star], radiusPixels: int, sensorSaturationValue: int) -> ([Star], float, float, float):
		"""
			For each star in stars, extracts a cricle (denoted by radiusPixels) and looks for the largest value using
			using sensorSatValue as the maximum and converting to % of saturation

			Excludes stars radiuses that fall out of bounds or overlap other star radiuses

			fitsFile	= fits file name
			stars		= list of stars with xy positions already set
			radiusPixels	= must be > 0  and represents the radius around the star we're looking at
			sensorSatValue	= the maxmimum value the sensor can have for a pixel

			Returns:
				valid stars with peakSensor set to the % of sensor saturation within radius of the stars expected position
				background mean as % of sensor saturation
				background median as % of sensor saturation
				background stddev as % of sensor saturation
		"""

		# Create the mask
		diameter = radiusPixels * 2
		mask_circle = np.zeros((diameter, diameter), dtype=np.uint16)
		self.__drawCenterCircle(mask_circle, radiusPixels)

		fits_data = fits.getdata(fitsFile, ext = 0)
		width = fits_data.shape[1]
		height = fits_data.shape[0]

		# Calculate the background stats
		bkg_mean, bkg_median, bkg_stddev = sigma_clipped_stats(fits_data, sigma=3.0)
		bkg_mean = (bkg_mean / sensorSaturationValue) * 100.0
		bkg_median = (bkg_median / sensorSaturationValue) * 100.0
		bkg_stddev = (bkg_stddev / sensorSaturationValue) * 100.0

		quadtree = Index(bbox = (0, 0, width, height))

		# Create a quad tree of possible stars
		possibleStars = []
		for star in stars:
			# Extract rectangle around star
			x1 = int(round(star.xy[0] - radiusPixels))
			x2 = int(round(star.xy[0] + radiusPixels))
			y1 = int(round(star.xy[1] - radiusPixels))
			y2 = int(round(star.xy[1] + radiusPixels))
	
			# If the rectangle is out of range of the frame, ignore
			if x1 < 0 or x2 >= width or y1 < 0 or y2 >= height:
				continue;

			star.bbox = (x1, y1, x2, y2)
			possibleStars.append(star)
			
			quadtree.insert(len(possibleStars)-1, star.bbox)

		# Run through each possible star and check if it overlaps others, if it does, we cull it
		isolatedStars = []
		for star in possibleStars:
			matches = quadtree.intersect(star.bbox)
			if len(matches) == 1:
				# If no other stars overlap 

				# Extract the region containing the star
				region = fits_data[star.bbox[1]:star.bbox[3], star.bbox[0]:star.bbox[2]]

				# Mask the region
				region = np.where(mask_circle == 1, region, 0)

				# Find the maximum value in the region
				star.peakSensor = (np.max(region) / sensorSaturationValue) * 100.0

				isolatedStars.append(star)

		return isolatedStars, bkg_mean, bkg_median, bkg_stddev



	def findStarsInArea(self, raRange: (float,float), decRange: (float, float)) -> [Star]:
		"""
			Find all stars within an area specified by the raRange and decRange

			Parameters:
				raRange:	Tuple(lower,upper) 0 - 360.0 (icrs)
				decRange:	Tuple(lower,upper) -90.0 - 90.0 (icrs)

			Returns:
				List of stars in this area, note that due to proper motion and rounding to the nearest dec/ra block,
				more stars will be returned than requested.
				Warning: Most of GAIA is J2016 and the results will need converting back to ICRS
		"""
		
		raLower  = raRange[0]
		raUpper  = raRange[1]
		decLower = decRange[0]
		decUpper = decRange[1]
		
		if raLower > raUpper:
			raise ValueError('raRange: start > end')
		if decLower > decUpper:
			raise ValueError('decRange: start > end')

		# Adjust RA and DEC for proper motion radius between 2016(Gaia) and 2000(icrs)
		pm_radius_deg = self.J2016_J2000_PROPER_MOTION_RADIUS/3600.0

		# In ra/dec are now out of range, pull the back in
		raLower  -= pm_radius_deg
		if raLower < 0:
			raLower = 0

		raUpper  += pm_radius_deg
		if raUpper > 360:
			raUpper = 360

		decLower -= pm_radius_deg
		if decLower < -90:
			decLower = -90

		decUpper += pm_radius_deg
		if decUpper > 90:
			decUpper = 90

		# Get the stars
		stars = []
		decZones = self.__getDecZones(decLower, decUpper)
		for decZone in decZones:
			if self.debug:
				print('\nDec Zone: %d' % decZone)
			zoneIndexStart = 361 * decZone
			(startRecord, endRecord) = self.__getStartEndRecord(zoneIndexStart, raLower, raUpper)
			stars += self.__readRecords(startRecord, endRecord)

		return stars


	def __getDecZones(self, startDec, endDec) -> list:
		if self.debug:
			print('DEC Region:         %0.6f->%0.6f' % (startDec, endDec))
		startDec	= math.floor(startDec * 2) / 2.0	# Round down startDec to 0.5deg intervals
		endDec		= math.ceil( endDec   * 2) / 2.0	# Round up endDec to 0.5deg intervals
		if self.debug:
			print('DEC Region Rounded: %0.2f->%0.2f' % (startDec, endDec))

		decZones = []
		dec = startDec
		while dec < endDec:
			decZone = 179 - int(2.0 * dec)
			#if dec < 0:
			#	decZone += 1
			decZones.append(decZone)

			dec += 0.5
		
		return decZones
		

	def __getStartEndRecord(self, zoneIndexStart, startRa, endRa):
		""" ra is in 360deg, startRa->endRa  (endRa is not inclusive) """
		if self.debug:
			print('RA Region:         %0.6f->%0.6f' % (startRa, endRa))
		startRa	= int(math.floor(startRa / 4.0) * 4.0)	# Round down startDec to 4deg intervals
		endRa	= int(math.ceil( endRa   / 4.0) * 4.0)	# Round up endDec to 4deg intervals
		if self.debug:
			print('RA Region Rounded: %d->%d' % (startRa, endRa))

		fp = open(self.fname_index, 'rb')

		fp.seek((zoneIndexStart + startRa) * 4)
		data = fp.read(4)
		(startRecord, ) = struct.unpack('=i', data)

		fp.seek((zoneIndexStart + endRa) * 4)
		data = fp.read(4)
		(endRecord, ) = struct.unpack('=i', data)
		
		fp.close()

		if self.debug:
			print('Records:           %d->%d' % (startRecord, endRecord))

		return (startRecord, endRecord)


	def __catByIdNum(self, catId, catNum) -> str:
		""" Returns the catlogue identifier by the id and num """
		catNum = str(catNum)

		if	catId == 0:
			return 'Unmatched'
		elif	catId == 2:
			return 'HIP ' + catNum
		elif	catId == 3:
			return 'TYC %s-%s-1' % (catNum[0:4], str(int(catNum[4:])))	# This is Tycho 2
		elif	catId == 4:
			return 'TYC %s-%s-2' % (catNum[0:4], str(int(catNum[4:])))	# This is Tycho 2
		elif	catId == 5:
			return 'TYC %s-%s-3' % (catNum[0:4], str(int(catNum[4:])))	# This is Tycho 2
		elif	catId == 6:
			return 'UCAC4 %s-%s' % (catNum[0:3], catNum[3:])


	def __readRecords(self, startRecord, endRecord) -> list:
		RECORD_LEN = 58

		records = []
		
		fp = open(self.fname_data, 'rb')
		fp.seek(startRecord * RECORD_LEN)
		
		for r in range(startRecord, endRecord):
			data = fp.read(RECORD_LEN)

			entry = {}

			(
				entry['ra'],			\
				entry['ra2'],			\
				entry['dec'],			\
				entry['dec2'],			\
				entry['parallax'],		\
				entry['pm_ra'],			\
				entry['pm_dec'],		\
				entry['rv'],			\
				entry['epoch'],			\
				entry['mag_bp'],		\
				entry['mag_g'],			\
				entry['mag_rp'],		\
				entry['e_ra'],			\
				entry['e_dec'],			\
				entry['e_parx'],		\
				entry['e_pm_ra'],		\
				entry['e_pm_dec'],		\
				entry['e_rv'],			\
				entry['reliability_indicator'],	\
				entry['flags'],			\
				entry['star_diameter'],		\
				entry['g_version'],		\
				entry['source_id'],		\
				entry['cat_id'],		\
				entry['cat_num']		\
			)  = struct.unpack('=iBiBHiihhhhhHHHHHBBBBBQBI', data)

			# Ra/Dec are in mas, add on ra2/dec2 (4 umas)
			ra  = entry['ra'] + entry['ra2'] * 0.004 
			dec = entry['dec'] + entry['dec2'] * 0.004 

			# Dec/Ra are in mas, conert to degrees
			ra  /= 3600000
			dec /= 3600000

			star = Star(entry['source_id'], ra, dec, 2000 + entry['epoch'] * 0.001, entry['mag_bp']/1000.0, entry['mag_g']/1000.0, entry['mag_rp']/1000.0, (entry['reliability_indicator'] / 255.0) * 12.6 , entry['flags'], entry['star_diameter'] * 0.2, entry['g_version'], self.__catByIdNum(entry['cat_id'], entry['cat_num']), r, (entry['parallax'] * 12.5) / 1000, entry['pm_ra'] / 1000, entry['pm_dec'] / 1000)

			records.append(star)

			if self.debug:
				print(star)
				print(entry)

		return records


	def __get_catalog_fnames(self, catalog):
		""" Returns """
		self.fname_data 	= None
		self.fname_index 	= None
		self.fname_hip_index	= None
		self.fname_ucac4_index	= None
		self.fname_tyc_index	= None

		for c in self.CATALOGS:
			if c['name'] == catalog:
				self.fname_data		= '/media/pi/ASTRID/catalogs/daveherald/' + c['fname_data']
				self.fname_index	= '/media/pi/ASTRID/catalogs/daveherald/' + c['fname_index']
				self.fname_hip_index	= '/media/pi/ASTRID/catalogs/daveherald/' + c['fname_hip_index']
				self.fname_ucac4_index	= '/media/pi/ASTRID/catalogs/daveherald/' + c['fname_ucac4_index']
				self.fname_tyc_index	= '/media/pi/ASTRID/catalogs/daveherald/' + c['fname_tyc_index']
				break


	def findHipparcosById(self, id: str) -> Star:
		""" Returns None if hipparcos id is not found """

		num = int(id.replace('HIP ', ''))

		# Obtain the GAIA catalog record number from the HIP index
		fp = open(self.fname_hip_index, 'rb')

		fp.seek((num-1) * 4)
		data = fp.read(4)
		(recordNum, ) = struct.unpack('=i', data)
	
		fp.close()
		
		if recordNum == 0:
			return None

		stars = self.__readRecords(recordNum, recordNum + 1)

		return stars[0]


	def findUCAC4ById(self, id: str) -> Star:
		""" Returns None if ucac4 id is not found """

		ucac4split		= id.replace('UCAC4 ', '').split('-')
		ucac4Zone		= int(ucac4split[0])
		ucac4NumberInZone	= int(ucac4split[1])

		gaiaMaxZone = int(math.floor((900 - ucac4Zone) / 2.5))
		gaiaMinZone = int(math.floor((900.5 - ucac4Zone) / 2.5))

		if self.debug:
			print('GaiaMinZone:', gaiaMinZone)
			print('GaiaMaxZone:', gaiaMaxZone)

		fp = open(self.fname_ucac4_index, 'rb')

		fp.seek(1444 * (ucac4Zone-1) + 4)
		raIndex = 0
		while True:
			data = fp.read(4)
			(readIndexNum, ) = struct.unpack('=i', data)
			if readIndexNum >= ucac4NumberInZone:
				break
			raIndex += 1
		
			if raIndex >= 360:
				break
	
		fp.close()

		raIndex -= 4.0
		if raIndex < 0:
			raIndex = 356

		if self.debug:
			print('RaIndex:', raIndex)
		
		stars = []
		for decZone in range(gaiaMinZone, gaiaMaxZone+1):
			if self.debug:
				print('Dec Zone:', decZone)
			zoneIndexStart = 361 * decZone 
			(startRecord, endRecord) = self.__getStartEndRecord(zoneIndexStart, raIndex, raIndex + 3.9)
			stars += self.__readRecords(startRecord, endRecord + 1)

		if self.debug:
			print('ID:', id)
		for star in stars:
			if star.catalog_id == id:
				return star

		return None
		

	def findTychosById(self, id: str) -> Star:
		tycsplit = id.replace('TYC ', '').split('-')
		tycRegion = int(tycsplit[0])

		fp = open(self.fname_tyc_index, 'rb')
		fp.seek((tycRegion-1) * 16)
		data = fp.read(16)
		fp.close()
		(raWesternLimit, raEasternLimit, decNorthernLimit, decSouthernLimit) = struct.unpack('=ffff', data)
		if self.debug:
			print('RaWesternLimit:', raWesternLimit)
			print('RaEasternLimit:', raEasternLimit)
			print('DecNorthernLimit:', decNorthernLimit)
			print('DecoSouthernLImit:', decSouthernLimit)

		# Make sure the ra/dec ranges are ascending
		if raWesternLimit < raEasternLimit:
			raRange = (raWesternLimit, raEasternLimit)
		else:
			raRange = (raEasternLimit, raWesternLimit)

		if decNorthernLimit < decSouthernLimit:
			decRange = (decNorthernLimit, decSouthernLimit)
		else:
			decRange = (decSouthernLimit, decNorthernLimit)

		stars = self.findStarsInArea(raRange, decRange)
		for star in stars:
			if star.catalog_id == id:
				return star
		
		return None


	def findGaiaById(self, id: str) -> Star:
		source_id = int(id.replace('EDR3 ', ''))

		# Extract the healpix from the source id
		# Reference: https://gea.esac.esa.int/archive/documentation/GDR2/Gaia_archive/chap_datamodel/sec_dm_main_tables/ssec_dm_gaia_source.html
		healpix = int(source_id / 34359738368)
		#print('HealPix', healpix)

		centerHealpix = cdshealpix.healpix_to_skycoord(healpix, depth=12)
		centerHealpix = (centerHealpix.ra.value[0], centerHealpix.dec.value[0])
		#print('Ra:', centerHealpix[0])
		#print('Dec:', centerHealpix[1])

		# At order 12, each healpix is about 0.7 arcmin square, so we can determine the limits,
		# add on 0.5 arcmin in both directions
		pixel_radius_deg = 0.5/60.0
		raRange = (centerHealpix[0] - pixel_radius_deg, centerHealpix[0] + pixel_radius_deg)
		decRange = (centerHealpix[1] - pixel_radius_deg, centerHealpix[1] + pixel_radius_deg)

		stars = self.findStarsInArea(raRange, decRange)
		for star in stars:
			if star.source_id == source_id:
				return star
		return None


	def findStarById(self, id: str) -> Star:
		"""
			Finds a star by it's id, examples:
				HIP 1234567
				UCAC4 123-123456	(2nd number is zero padded)
				TYC 1234-56789-1	(or -2 or -3)  Note: 56789 is NOT zero padded
				EDR3 12345345348	(variable length number, not zero padded)
	
			Returns None in case of error or failure to find
		"""

		if   id.startswith('HIP '):
			return self.findHipparcosById(id)
		elif id.startswith('UCAC4 '):
			return self.findUCAC4ById(id)
		elif id.startswith('TYC '):
			return self.findTychosById(id)
		elif id.startswith('EDR3 '):
			return self.findGaiaById(id)
		else:
			raise ValueError('Unknown Star Catalog')


#starLookup = StarLookup()

#ids = ['HIP 117053', 'UCAC4 451-000373', 'UCAC4 452-000700', 'TYC 4627-82-1', 'HIP 6793', 'HIP 6911', 'HIP 2942', 'TYC 1800-1974-1', 'TYC 4212-1079-1', 'EDR3 2545442368322040320', 'EDR3 2545440581615646208', 'EDR3 2543667309878982912', 'EDR3 575894439391955584']
 
#for id in ids:
#	star = starLookup.findStarById(id)
#	star.epochPropogateToJ2000()
#	print('Finding: %-24s Result: %s' % (id, star))
