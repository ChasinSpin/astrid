import math
from astsite import AstSite
import astropy.units as u
from datetime import datetime, timezone, timedelta
from astropy.time import Time
from settings import Settings
from astropy.utils.iers.iers import conf
from astropy.coordinates import ICRS, FK4, FK5, TETE, AltAz, SkyCoord, EarthLocation


"""
	Coordinates are always stored internally in ICRS and 360 deg

	Supported frames and terms:
		ICRS (coordinate system) also confusingly known as J2000
			Equinox: J2000
			Location: As seen from the sun
			Reference: http://astro.vaporia.com/start/icrs.html

		FK5 (coordinate system) also confusingly known as J2000
			Equinox: J2000
			Location: Celestial coordinate system based on the location of the FK5 catalogues objects
			Reference: http://astro.vaporia.com/start/celestialreferenceframe.html

		FK4 (coordinate system)
			Equinox: B1950.0
			Location: Celestial coordinate system based on the location of the FK4 catalogues objects
			Reference" http://astro.vaporia.com/start/celestialreferenceframe.html

		Topocentric (also known as JNOW Reference: https://ascom-standards.org/Help/Developer/html/72A95B28-BBE2-4C7D-BC03-2D6AB324B6F7.htm)
			This implementation accounts for precession, nutation and atmospheric abberation
			Equinox: Now
			Location: Site

		J2000/B1950.0 is the epoch (equinox) in which the catalogue is in

		FK5(optical observations) and ICRS(radio observations) are different reference systems (but difference between both is small (<80 arc secs)) ICRS is the most modern
		Reference: https://astronomy.stackexchange.com/questions/33793/difference-between-j2000-fk5-and-icrs-coordinate-systems-which-one-does-the-ya

		JNow should be known as Topocentric, essentially it's another equinox.
		Topocentric is a better term as it accounts for precession, nutation and atmospheric abberation
		Reference: https://ascom-standards.org/Help/Developer/html/72A95B28-BBE2-4C7D-BC03-2D6AB324B6F7.htm

		Mounts typically use JNOW but also may use J2000

"""


class AstCoord:

	SIDEREAL_DAY_LENGTH = 23.9344696

	def __init__(self, skyCoord: SkyCoord):
		""" Use the class methods starting 'from' below to instantiate object, DO NOT USE THIS """
		self.skyCoord = skyCoord
		#print("Creating %s (360 deg)" % self.skyCoord)


	def __str__(self):
		return str(self.skyCoord)


	@classmethod
	def fromHMS(cls, ra: (float, int, float), dec: (float, int, float), frame: str):
		ra = '%0.0fh%dm%0.5f' % (ra[0], ra[1], ra[2])
		dec = '%0.0fd%dm%0.5f' % (dec[0], dec[1], dec[2])
		skyCoord = SkyCoord(ra, dec, frame=frame)
		return cls(skyCoord.transform_to('icrs'))


	@classmethod
	def from360Deg(cls, ra: float, dec: float, frame: str):
		skyCoord = SkyCoord(ra, dec, frame=frame, unit="deg")
		return cls(skyCoord.transform_to('icrs'))


	@classmethod
	def from24Deg(cls, ra: float, dec: float, frame: str, jnow=False, obsdatetime = None):
		if jnow:
			# Transform to FK5 (as it's the only one we can do the equinox conversion on)
			# Without changing the coorindates.  We do the frame conversion later.
			if obsdatetime is None:
				now = Time(datetime.utcnow(), scale='utc', location = AstSite.location())
			else:
				now = Time(obsdatetime, scale='utc', location = AstSite.location())
			skyCoord = SkyCoord(ra, dec, frame='fk5', unit=(u.hourangle, u.deg), equinox=now)
			skyCoord = skyCoord.transform_to(FK5(equinox='J2000'))
			skyCoord = SkyCoord(skyCoord.ra.value, skyCoord.dec.value, frame=frame, unit=(u.deg, u.deg))
		else:
			skyCoord = SkyCoord(ra, dec, frame=frame, unit=(u.hourangle, u.deg))

		return cls(skyCoord.transform_to('icrs'))


	def __raDec360Deg(self, frame: str, jnow = False, obsdatetime = None):
		coord = self.skyCoord.transform_to(frame)
		now = None
		
		# If jnow is set, change to topocentric coordinates
		if jnow:
			# Transform to FK5 (as it's the only one we can do the equinox conversion on)
			# Without changing the coorindates
			coord = SkyCoord(coord.ra.value, coord.dec.value, frame='fk5', unit="deg")
			if obsdatetime is None:
				now = Time(datetime.utcnow(), scale='utc', location = AstSite.location())
			else:
				now = Time(obsdatetime, scale='utc', location = AstSite.location())
			coord = coord.transform_to(FK5(equinox=now))

		return (coord, now)


	def raDec360Deg(self, frame: str, jnow = False, obsdatetime = None):
		(coord, _) = self.__raDec360Deg(frame, jnow, obsdatetime)
		return (coord.ra.value, coord.dec.value)
		

	def raDec24Deg(self, frame: str, jnow = False, obsdatetime = None):
		(coord, _) = self.__raDec360Deg(frame, jnow, obsdatetime)
		ra24 = (coord.ra.value / 360.0) * 24.0
		return (ra24, coord.dec.value)


	def raDecHMS(self, frame: str, jnow = False, obsdatetime = None):
		(coord, _) = self.__raDec360Deg(frame, jnow, obsdatetime)
		dms = coord.dec.dms
		dms = (dms[0], abs(dms[1]), abs(dms[2]))
		return (coord.ra.hms, dms)


	def raDecHMSStr(self, frame: str, jnow = False, obsdatetime = None):
		(coord, _) = self.__raDec360Deg(frame, jnow, obsdatetime)
		(raDeg, raMin, raSec)  = coord.ra.hms
		(decDeg, decMin, decSec)  = coord.dec.dms
		decMin = abs(decMin)
		decSec = abs(decSec)

		raMin = abs(raMin)
		raSec = abs(raSec)
		decMin = abs(decMin)
		decSec = abs(decSec)

		raStr = '%0.0fh%02dm%#08.5f' % (raDeg, raMin, raSec)
		decStr = '%0.0fd%02dm%#07.4f' % (decDeg, decMin, decSec)
		if decDeg > 0:
			decStr = '+' + decStr
		return (raStr, decStr)


	def raDecStrForSettingFormat(self, frame: str, jnow = False, obsdatetime = None):
		ra = ''
		dec = ''
		radec_format = Settings.getInstance().camera['radec_format']

		if radec_format == 'hour':
			(ra, dec) = self.raDec24Deg(frame, jnow = jnow, obsdatetime = obsdatetime)
			ra = '%0.7f' % ra
			dec = '%0.7f' % dec
		elif radec_format == 'hmsdms':
			(ra, dec) = self.raDecHMSStr(frame, jnow = jnow, obsdatetime = obsdatetime)
		elif radec_format == 'deg':
			(ra, dec) = self.raDec360Deg(frame, jnow = jnow, obsdatetime = obsdatetime)
			ra = '%0.7f' % ra
			dec = '%0.7f' % dec

		return (ra, dec)


	# Returns altitude and azimuth including refraction corrections (pressure, temperture, humidity)
	# This is jnow by definition	

	def altAzRefractedByLocation(self, location: EarthLocation, frame: str, obsdatetime = None):
		(coord, now) = self.__raDec360Deg(frame, jnow = True, obsdatetime = obsdatetime)
		# Reference: https://stackoverflow.com/questions/60305302/converting-equatorial-to-alt-az-coordinates-is-very-slow
		conf.remote_timeout = 0.1
		conf.auto_download = False
		altAz = coord.transform_to(AltAz(obstime=now, location=AstSite.location(), pressure=AstSite.pressure*u.pascal, temperature=AstSite.temperature*u.Celsius, relative_humidity=AstSite.rh, obswl=0.65*u.micron))
		conf.remote_timeout = 10.0
		conf.auto_download = True
		return (altAz.alt.deg, altAz.az.deg)


	def altAzRefracted(self, frame: str, obsdatetime = None):
		location = AstSite.location()
		return self.altAzRefractedByLocation(location, frame, obsdatetime)


	def meridianFlipMins(self):
		# Reference: https://en.wikipedia.org/wiki/Hour_angle

		# Calculate the Local Sidereal Time and then the Local Hour Angle of the object
		observing_time = Time(datetime.utcnow(), scale='utc', location=AstSite.location())

		try:
			local_sidereal_time = observing_time.sidereal_time('mean')
		except:
			conf.auto_max_age = None
			return 0

		(ra, dec) = self.raDec24Deg('icrs')
		local_hour_angle = local_sidereal_time.hour - ra
		#print("Observing Time:", observing_time)
		#print("Local Sidereal Time:", local_sidereal_time)
		#print("Local Hour Angle:", local_hour_angle)

		meridianFlipInMins = -local_hour_angle * 60.0

		return meridianFlipInMins



	def prepointCoords(self, targetInFOVTime: datetime,  prepointTime: datetime): 
		print('***** targetInFOVTime', targetInFOVTime)
		# Get the coordinate  of the target in JNow for the event time
		(coord, event_time) = self.__raDec360Deg('icrs', jnow = True, obsdatetime = targetInFOVTime)
		print('***** event_time', event_time)

		# Reference: https://stackoverflow.com/questions/60305302/converting-equatorial-to-alt-az-coordinates-is-very-slow
		conf.remote_timeout = 0.1
		conf.auto_download = False

		# Get the AltAz Coordinate for the target at the event time
		event_altAz = coord.transform_to(AltAz(obstime=event_time, location=AstSite.location(), pressure=AstSite.pressure*u.pascal, temperature=AstSite.temperature*u.Celsius, relative_humidity=AstSite.rh, obswl=0.65*u.micron))
		print('**** event_altAz:', event_altAz)

		prepoint_altAz = SkyCoord(AltAz(obstime = prepointTime, az = event_altAz.az, alt = event_altAz.alt, location=AstSite.location(), pressure=AstSite.pressure*u.pascal, temperature=AstSite.temperature*u.Celsius, relative_humidity=AstSite.rh, obswl=0.65*u.micron))
		prepoint_icrs = prepoint_altAz.transform_to('icrs')

		print("**** prepointTime:", prepointTime)
		print("**** prepointAltAz:", prepoint_altAz)

		# Reference: https://stackoverflow.com/questions/60305302/converting-equatorial-to-alt-az-coordinates-is-very-slow
		conf.remote_timeout = 10.0
		conf.auto_download = True

		prepoint_coords = AstCoord(prepoint_icrs)

		return prepoint_coords


	def angular_separation(self, to_coord):
		# Returns angular separation from this coordinate to to_coord in degrees
		return self.skyCoord.separation(to_coord.skyCoord).deg


	def raDec360DegTete(self, obsdatetime):
		"""
			Returns the RA/DEC in 360deg for the TETE frame (apparent RA/DEC) given the observation date.
			This is used primarily for asteroid path calculation
		"""
		coord = self.skyCoord.transform_to(TETE(obstime = obsdatetime))
		return (coord.ra.value, coord.dec.value)


	def fastRaDecToAltAz(self, lat, lon, obsdatetime):
		"""
			Reference: https://astrogreg.com/convert_ra_dec_to_alt_az.html
			Used primarily for speed
			Requires apparentRa/Dec
		"""

		# Convert Ra/Dec/Lat/Lon to radians
		(apparentRa, apparentDec) = (self.skyCoord.ra.value, self.skyCoord.dec.value)

		apparentRa      = math.radians(apparentRa)
		apparentDec     = math.radians(apparentDec)
		lat             = math.radians(lat)
		lon             = math.radians(lon)

		jd_ut = (obsdatetime - datetime(2001,4,1,0,0,0, 0, tzinfo = timezone.utc)) / timedelta(days=1) + 2452000.5

		# Meeus 13.5 and 13.6, modified so West longitudes are negative and 0 is North
		gmst			= self.__fastGreenwichMeanSiderealTime(jd_ut)
		localSiderealTime	= (gmst + lon) % (2.0 * math.pi)

		H			= localSiderealTime - apparentRa
		if H < 0.0:
			H += 2.0 * math.pi
		if H > math.pi:
			H = H - 2.0 * math.pi

		az	= (math.atan2(math.sin(H), math.cos(H) * math.sin(lat) - math.tan(apparentDec) * math.cos(lat)))
		alt	= (math.asin(math.sin(lat) * math.sin(apparentDec) + math.cos(lat) * math.cos(apparentDec) * math.cos(H)))
		az	-= math.pi

		if az < 0.0:
			az += 2.0 * math.pi
			
		alt = math.degrees(alt)
		az = math.degrees(az)

		return (alt, az)


	def __fastGreenwichMeanSiderealTime(self, jd):
		# "Expressions for IAU 2000 precession quantities" N. Capitaine1,P.T.Wallace2, and J. Chapront
		t = ((jd - 2451545.0)) / 36525.0

		gmst = self.__fastEarthRotationAngle(jd) + (0.014506 + 4612.156534*t + 1.3915817*t*t - 0.00000044*t*t*t - 0.000029956*t*t*t*t - 0.0000000368*t*t*t*t*t)/60.0/60.0*math.pi/180.0 # eq 42
		gmst %= 2.0 * math.pi
		if gmst < 0:
			gmst += 2.0 * math.pi

		return gmst


	def __fastEarthRotationAngle(self, jd):
		# IERS Technical Note No. 32

		t = jd - 2451545.0
		f = jd % 1.0

		theta = 2.0 * math.pi * (f + 0.7790572732640 + 0.00273781191135448 * t)	# eq 14
		theta %= 2.0 *math.pi
		if theta < 0.0:
			theta += 2.0 * math.pi

		return theta



"""
AstSite.set(51.3473, -114.2893, 1000.0)
vega = AstCoord.fromHMS(ra=(18, 36, 57.96), dec=(38, 47, 19.8), frame='icrs')
print('ICRS 360:', vega.raDec360Deg(frame='icrs'))
print('ICRS 24:', vega.raDec24Deg(frame='icrs'))
print('ICRS HMS:', vega.raDecHMS(frame='icrs'))
print('ICRS HMSStr:', vega.raDecHMSStr(frame='icrs'))

print('JNOW 360:', vega.raDec360Deg(frame='icrs', jnow=True))
print('JNOW 24:', vega.raDec24Deg(frame='icrs', jnow=True))
print('JNOW HMS:', vega.raDecHMS(frame='icrs', jnow=True))
print('JNOW HMSStr:', vega.raDecHMSStr(frame='icrs', jnow=True))

print('AltAz Refracted:', vega.altAzRefracted(frame='icrs'))
"""
