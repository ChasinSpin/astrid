import math
import struct
from astcoord import AstCoord
from astropy.coordinates import ICRS, FK5, SkyCoord


class Star():

	def __init__(self, source_id, ra, dec, epoch, mag_bp, mag_g, mag_rp, ruwe, flags, diameter, gaia_version, catalog_id, record_num):
		super().__init__()

		self.source_id		= source_id
		self.ra			= ra		# 360 deg
		self.dec		= dec		# +-90 deg
		self.epoch		= epoch		# Year
		self.mag_bp		= mag_bp
		self.mag_g		= mag_g		# Commonly visual magnitude
		self.mag_rp		= mag_rp
		self.ruwe		= ruwe		# Incorrect, investigate
		self.flags		= flags
		self.diameter		= diameter	# mas
		self.gaia_version	= gaia_version
		self.catalog_id		= catalog_id
		self.record_num		= record_num

		# The ra/dec are specified according to the epoch (equinox)
		self.coord=None
		#self.coord = SkyCoord(self.ra, self.dec, frame='fk5', equinox='J%0.3f' % self.epoch, unit='deg')
		#fk5_j2000 = FK5(equinox='J2000')
		#self.coord = self.coord.transform_to(fk5_j2000)

	"""


        @classmethod
        def fromHMS(cls, ra: (int, int, float), dec: (int, int, float), frame: str):
                ra = '%dh%dm%0.5f' % (ra[0], ra[1], ra[2])
                dec = '%dd%dm%0.5f' % (dec[0], dec[1], dec[2])
                skyCoord = SkyCoord(ra, dec, frame=frame)
                return cls(skyCoord.transform_to('icrs'))


        @classmethod
        def from360Deg(cls, ra: float, dec: float, frame: str):
                skyCoord = SkyCoord(ra, dec, frame=frame, unit="deg")
                return cls(skyCoord.transform_to('icrs'))
	"""



	def __str__(self):
		return 'gaia_id:%-19d gaia_version:%d catalog_id:%-16s ra:%-13.9f dec:%-12.9f epoch:%-0.2f mag_v:%-5.2f ruwe:%-6.3f flags:0x%02X diameter:%-5.3f record_num:%-8d skyCoord:%s' % \
			(self.source_id, self.gaia_version, self.catalog_id, self.ra, self.dec, self.epoch, self.mag_g, self.ruwe, self.flags, self.diameter, self.record_num, self.coord)



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


	def findStarInFOV(self,  centerCoord: AstCoord, rotation: float, fieldOfView: (float,float)) -> [Star]:
		""""
			Finds stars in the FOV

			Parameters:
				centerCoord	= Plate Solve Center
				rotation	= Plate Solve Rotation
				fieldOfView	= (width, height) - degrees

			Returns:
				list of stars
		"""

		pass


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

			star = Star(entry['source_id'], ra, dec, 2000 + entry['epoch'] * 0.001, entry['mag_bp']/1000.0, entry['mag_g']/1000.0, entry['mag_rp']/1000.0, (entry['reliability_indicator'] / 255.0) * 12.6 , entry['flags'], entry['star_diameter'], entry['g_version'], self.__catByIdNum(entry['cat_id'], entry['cat_num']), r)

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


	# DISABLED FOR NOW, as there doesn't seem to be a way to get to record id from source id
	#def findGaiaById(self, id: str) -> Star:
	#	pass


	def findStarById(self, id: str) -> Star:
		"""
			Finds a star by it's id, examples:
				HIP 1234567
				UCAC4 123-123456	(2nd number is zero padded)
				TYC 1234-56789-1	(or -2 or -3)  Note: 56789 is NOT zero padded
				EDR3 12345345348	(variable length number, not zero padded)
		"""

		if   id.startswith('HIP '):
			return self.findHipparcosById(id)
		elif id.startswith('UCAC4 '):
			return self.findUCAC4ById(id)
		elif id.startswith('TYC '):
			return self.findTychosById(id)
		# DISABLED FOR NOW, as there doesn't seem to be a way to get to record id from source id
		#elif id.startswith('EDR3 '):
		#	return self.findGaiaById(id)
		else:
			raise ValueError('Unknown Star Catalog')


starLookup = StarLookup()

##ids = ['EDR3 2545442368322040320', 'HIP 117053', 'UCAC4 451-000373', 'TYC 2010-73-1']
ids = ['HIP 117053', 'UCAC4 451-000373', 'UCAC4 452-000700', 'TYC 4627-82-1', 'HIP 6793', 'HIP 6911', 'HIP 2942', 'TYC 1800-1974-1', 'TYC 4212-1079-1']
 
for id in ids:
	print('Finding: %-17s Result: %s' % (id, starLookup.findStarById(id)))
