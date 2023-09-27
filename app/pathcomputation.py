#!/usr/bin/env python3

# Credit: Thanks to Steve Preston for these Occultation Path Calculations

# Running unit tests:
#	python3 -m pytest pathcomputation.py -v


import sys
import math
from datetime import datetime, timedelta
from astcoord import AstCoord
from astutils import AstUtils

"""
Definitions:
	closest_approach	= (year, month, day and UT) of closest approach
	shadow_center		= (X,Y) coordinates of the asteroid shadow center, on the fundamental plane, at the time of closest approach (units = earth equatorial radius)
	dXY			= (dX, dY) coefficients for cubic polynomial equation of motion for asteroid shadow on fundemntal plane (time is in hours from geocentric close approach)
	d2XY			= (d2X, d2Y) coefficients for cubic polynomial equation of motion for asteroid shadow on fundemntal plane (time is in hours from geocentric close approach)
	d3XY			= (d3X, d3Y) coefficients for cubic polynomial equation of motion for asteroid shadow on fundemntal plane (time is in hours from geocentric close approach)
	starRaDec		= (ra, dec) Apparent position (apparent RA/DEC) at the time of the event (JNOW - topocentric)
"""



class PathComputation:

	C_BESS_A = 6378.14	# earth equatorial radius (km)
	C_BESS_B = 6356.755	# earth polar radius (km)


	def __init__(self, occelmnt: dict, calcApparentStar = True):
		"""
		Given an occelmnt dictionary, it creates an object to calculate path information for the occultation
	
		calcApparentStar:
			True = Apparent (JNOW) RA/DEC for the star is calculated via AstCoord (Astropy)
			False = Apparent (JNOW) RA/DEC for the star is taken from the occelmnt
		"""
	
		elements	= occelmnt['Occultations']['Event']['Elements'].split(',')
		star		= occelmnt['Occultations']['Event']['Star'].split(',')

		self.calcApparentStar	= calcApparentStar
		self.XatClosest		= float(elements[6])
		self.YatClosest		= float(elements[7])
		self.dX			= float(elements[8])
		self.dY			= float(elements[9])
		self.d2X		= float(elements[10])
		self.d2Y		= float(elements[11])
		self.d3X		= float(elements[12])
		self.d3Y		= float(elements[13])
		self.starCoord		= AstCoord.from24Deg(float(star[1]), float(star[2]), 'icrs')
	
		print('Star J2000:', self.starCoord.raDecHMSStr('icrs'))
		if not self.calcApparentStar:
			self.apparentStarCoord	= AstCoord.from24Deg(float(star[9]), float(star[10]), 'icrs')
			print('Star Apperent:', self.apparentStarCoord.raDecHMSStr('icrs'))

		# Calculate Fractional hour of closest approach
		utcTime = elements[5]
		utcHour = int(utcTime.split('.')[0])
		utcFractionalHour = float(utcTime) - float(utcHour)
		utcHourSecs = utcFractionalHour * 3600
		utcMins = int(utcHourSecs / 60)
		utcSecs = int(utcHourSecs - (utcMins * 60))

		self.dateTimeAtClosest = datetime(int(elements[2]), int(elements[3]), int(elements[4]), utcHour, utcMins, utcSecs, 0)
		#print("Closest Time:", self.dateTimeAtClosest)
		#print("Closest X:", self.XatClosest)
		#print("Closest Y:", self.YatClosest)

		self.centerPath = self.__calcCenterPath(1.0)
		print('Center path: start:%s end:%s # points:%d' % (str(self.centerPath['startDateTime']), str(self.centerPath['endDateTime']), len(self.centerPath['points'])))


	def centerOfAsteroidShadow(self, dteDate: datetime) -> (float, float):
		"""
		For a given utc date, calculate the Lat/Lon of the center of the asteroid shadow on earth	
		Returns: Tuple(lat,lon) or None is the shadow is not on earth

		for a given time T (UTC) and midT = time of closest geocentric approach
		compute the Greenwich Apparent Sidereal Time (GAST / GST) at time T 
		timeDiffHours = T - midT
		compute (CenterX, CenterY) = the fundamental plane coordinates of the center of the asteroid shadow at time T
			CenterX = X + dX * TimeH + d2X * TimeH * TimeH + d3X * TimeH * TimeH * TimeH
			CenterY = Y + dY * TimeH + d2Y * TimeH * TimeH + d3Y * TimeH * TimeH * TimeH
		compute (Lat,Long) = geodetic position of shadow center at intercept with Earth ellipsoid
			use CenterX, CenterY, GAST, and the apparent star position as inputs to the routine Bess_FtoGeodetic()
		"""

		timeDiffHours = (self.dateToJD(dteDate) - self.dateToJD(self.dateTimeAtClosest)) * 24.0
		#print('timeDiffHours:', timeDiffHours)

		centerX = self.XatClosest + self.dX * timeDiffHours + self.d2X * timeDiffHours * timeDiffHours + self.d3X * timeDiffHours * timeDiffHours * timeDiffHours
		centerY = self.YatClosest + self.dY * timeDiffHours + self.d2Y * timeDiffHours * timeDiffHours + self.d3Y * timeDiffHours * timeDiffHours * timeDiffHours
		#print("centerX:", centerX)
		#print("centerY:", centerY)

		if self.calcApparentStar:
			(starRA, starDEC) = self.starCoord.raDec360Deg('icrs', jnow = True, obsdatetime=dteDate)
		else:
			(starRA, starDEC) = self.apparentStarCoord.raDec360Deg('icrs')

		starRA = math.radians(starRA)
		starDEC = math.radians(starDEC)

		latlon = self.bess_FtoGeodetic(centerX, centerY, starRA, starDEC, self.dateToGAST(dteDate))

		if latlon is None:
			return None

		# lat/lon are in radians, convert to degrees
		return (math.degrees(latlon[0]), math.degrees(latlon[1]))


	def __calcCenterPath(self, intervalSecs: float) -> list:
		"""
		IMPORTANT: Doesn't factor in the shadow width, only the center point, this should probably be fixed to get accurate start/end times

		Searches from the time of closest approach in units of intervalSecs until the shadow is no longer on earth, building
		a track of lat/lon's and times. 

		Returns: Tuple(startTime, endTime, points)
			startTime	= Starting datetime of the shadow hiting earth
			endTime		= Ending datetime of the shadow hitting earth
			points		= list of (datetime, lat, lon)
		"""

		points = []

		microsecondsInterval = int(intervalSecs * 1000000)
		
		# Run the time backwards until we fall off the earth, building up the list
		dte = self.dateTimeAtClosest
		while True:
			latlon = self.centerOfAsteroidShadow(dte)
			if latlon is None:
				break
			points.append((dte, latlon[0], latlon[1]))

			# Setup next date
			dte -= timedelta(microseconds=microsecondsInterval)

		# Reverse the list so it's in time increasing order
		points.reverse()

		# Now run the time forwards until we fall off the earth, building up the list
		dte = self.dateTimeAtClosest + timedelta(microseconds=microsecondsInterval)
		while True:
			latlon = self.centerOfAsteroidShadow(dte)
			if latlon is None:
				break
			points.append((dte, latlon[0], latlon[1]))

			# Setup next date
			dte += timedelta(microseconds=microsecondsInterval)

		return {'startDateTime': points[0][0], 'endDateTime': points[-1][0], 'points': points}


	def timeAndChordDistanceForLocation(self, lat: float, lon: float) ->float:
		"""
		"""
		# Find the index in points of the minimum distance from lat/lon to the canter path
		closestIndex = 0
		closestDistance = sys.float_info.max

		for epochIndex in range(0, len(self.centerPath['points'])):
			epoch = self.centerPath['points'][epochIndex]
			distance = AstUtils.haversineDistance(epoch[1], epoch[2], lat, lon)
			if distance < closestDistance:
				closestIndex = epochIndex
				closestDistance = distance

		print(epochIndex)
		print(self.centerPath['points'][closestIndex][0])
	


	def dateToGAST(self, dteDate: datetime) -> float:
		"""
		Calculates Greenwich Apparent Sideral Time (GAST) in radians for a given utc date/time
			dteDate = datetime utc
			Returns: GAST in radians
		"""
		GMST = self.dateToGMST(dteDate)

		# Calculate the equation of the equinoxes
		(meanObq, nuObq, nuLon) = self.dateToEcliptic(dteDate)
		trueObq = meanObq + nuObq                 			# True obliquity
		equation_of_the_equinoxes = nuLon * math.cos(trueObq)

		#print("equation_of_the_eqinoxes:", (math.degrees(equation_of_the_equinoxes) * 3600) / 360.0 * 24.0)

		return GMST + equation_of_the_equinoxes				# Apparent Greenwich Sideral time at dteDate


	def dateToGMST(self, dteDate: datetime) -> float:
		"""
		Calculates Greenwich Mean Sideral Time (GMST) in radians for a given utc date/time
			dteDate = datetime utc
			Returns: GMST in radians
		"""

		# compute days since noon 2000 Jan 1 = JD 2451545.0
		totalDays = (dteDate - datetime(2000,1,1,12,0,0,0)) / timedelta(days=1)		# Fractional days

		T = totalDays / 36525.0								# number of tropical centuries
            
		# Compute gmst in degrees
		gmst = 280.46061837 + 360.98564736629 * totalDays
		gmst = gmst + 0.000387933 * T * T - (T * T * T) / 38710000.0

		# Limit to 0 to 360 deg range
		gmst = gmst % 360.0

		# convert to radians
		return math.radians(gmst)


	def __make2Pi(self, radians):
		# Modulu raidians to 0 to 2PI
		return radians % (math.pi * 2)
	

	def dateToJD(self, dteDate: datetime) -> float:
		"""
		Computes JD for given date/time
			dteDate = datetime utc
			Returns: JD	
		"""		

		totalDays = (dteDate - datetime(2001,4,1,0,0,0,0)) / timedelta(days=1)		# Fractional days

		return (totalDays + 2452000.5)


	def dateToEcliptic(self, dteDate: datetime) -> (float, float, float):
		"""
		Compute Mean Obliquity of the Ecliptic, Nutation in Longitude, and Nutation in Obliquity for given date/time
			dteDate = datetime utc to determine ecliptic parameters
			Returns: Tuple(MeanObliquity, NutationLongitude, NutationObliquity in radians (0 to 2*PI)
		"""

		# compute T = time elapsed since JD 2451545
		#	note: have not considered deltaT adjustment to compute this in ephemeris time instead of UT
		jdDate = self.dateToJD(dteDate)

		dblT = (jdDate - 2451545.0) / 36525.0

		# compute mean Long of ascending node of moon
		omega = 125.04452 - 1934.136261 * dblT + 0.0020708 * (dblT * dblT) + (dblT * dblT * dblT) / 450000.0	# deg
		omega = math.radians(omega)										# -> rad

		# compute mean long of the sun and moon
		LSun = 280.4665 + 36000.7698 * dblT									# deg
		LMoon = 218.3165 + 481267.8813 * dblT									# deg
		LSun = math.radians(LSun)	 									# -> rad
		LMoon = math.radians(LMoon)										# -> rad

		# compute mean obliquity
		meanObliquity = 84381.448										# 23deg 26' 21.448" in arcsec
		meanObliquity += -46.8150 * dblT - 0.00059 * (dblT * dblT) + 0.001813 * (dblT * dblT * dblT)		# arcsec
		meanObliquity = math.radians(meanObliquity) / 3600.0							# arcsec -> rad
		meanObliquity = self.__make2Pi(meanObliquity)

		# compute nutationLongitude
		nutationLongitude = -17.20 * math.sin(omega)
		nutationLongitude += -1.32 * math.sin(2.0 * LSun)
		nutationLongitude += -0.23 * math.sin(2.0 * LMoon)
		nutationLongitude += 0.21 * math.sin(2.0 * omega)							# arcsec
		nutationLongitude = math.radians(nutationLongitude) / 3600.0						# arcsec -> rad
		nutationLongitude = self.__make2Pi(nutationLongitude)
		if nutationLongitude > math.pi:
			nutationLongitude -= 2.0 * math.pi								# makeit +/-

		nutationObliquity = 9.20 * math.cos(omega)
		nutationObliquity += 0.57 * math.cos(2.0 * LSun)
		nutationObliquity += 0.10 * math.cos(2.0 * LMoon)
		nutationObliquity += -0.09 * math.cos(2.0 * omega)							# arcsec
		nutationObliquity = math.radians(nutationObliquity) / 3600.0						# arcsec -> rad
		nutationObliquity = self.__make2Pi(nutationObliquity)
		if nutationObliquity > math.pi:
			nutationObliquity -= 2.0 * math.pi								# make +/-

		return (meanObliquity, nutationObliquity, nutationLongitude)


	"""
	BESSELIAN functions for Asteroid occultations

	These functions compute coordinate transformations between
	geodetic coordinates and Bessel's fundamental plane.  They
	assume the following parameters for the Earth's oblate spheroid
	a= equatorial radius = 6378.14 km
	b= polar radius = 6356.755 km
	"""

	def bess_FtoGeodetic(self, X: float, Y: float, RA: float, DE: float, GST: float) -> (float, float):
		"""
		Determines geodetic coordinate for the shadow intercept of point in the fundamental plane

			X,Y		= fundamental plane (x,y) coordinates of shadow's intercept with fundamental plane (units = earth equatorial radius).
			RA		= RA of star (radians)
			DE		= DE of star (radians)
			GST		= Greenwich Sidereal Time (radians)

			Returns: Tuple(lat, lon) or None if shadow is not on earth
			Where:
				lat, lon = geodetic Lat, Lon for point on Earth (radians, E Lon)

			note: see file "Asteroid Occultation Besselian Equations.doc" for more info
		"""	

		# Step 1: compute e, rho1, eta1, zeta1 and check for intersection with ellipsoid
		e = math.sqrt(1.0 - (PathComputation.C_BESS_B * PathComputation.C_BESS_B) / (PathComputation.C_BESS_A * PathComputation.C_BESS_A))

		rho1 = math.sqrt(1.0 - e * e * math.cos(DE) * math.cos(DE))

		eta1 = Y / rho1

		zeta1 = 1.0 - X * X - eta1 * eta1		# actually square of zeta1 here
		if zeta1 >= 0:
			zeta1 = math.sqrt(zeta1)

			# Step 2: calculate sinphi1, cosphi1, and theta
			sinD1 = math.sin(DE) / rho1
			cosD1 = math.sqrt(1.0 - e * e) * math.cos(DE) / rho1
	
			theta = math.atan2(X, (zeta1 * cosD1 - eta1 * sinD1))
	
			sinphi1 = eta1 * cosD1 + zeta1 * sinD1
			cosphi1 = X / math.sin(theta)
	
			# Step 3: calculate lat and long
			lat = math.atan2(sinphi1, math.sqrt(1.0 - e * e) * cosphi1)
			lon = theta - GST + RA
	
			# Make sure Longitude is in range [-Pi, Pi]
			lon = self.__make2Pi(lon)
			if lon > math.pi:
				lon = lon - 2.0 * math.pi
		else:
			# shadow does not intercept earth's ellipsoid
			return None

		return (lat, lon)


	def bess_GeodeticToF(lat: float, lon: float, height: float, RA: float, DE: float, GST: float) -> (float, float, float):
		"""
		Determines geodetic coordinate for the shadow intercept of a point in the fundamental plane
			lon, lat	= geodetic Lat, Long for point on Earth (radians, E Long)
			height		= height about ellipsoid (km)
			RA		= RA of star (radians)
			DE		= DE of star (radians)
			GST		= Greenwich Sidereal Time (radians)

			Returns: Tuple(X, Y, Z)
			Where:
				X,Y,Z	= (x,y,z) coordinates of intercept with fundamental plane

       				Notes: units = earth equatorial radius

		note: see file "Asteroid Occultation Besselian Equations.doc" for more info
		"""

		# Step 1
		u = math.atan2(PathComputation.C_BESS_B * math.tan(lat), PathComputation.C_BESS_A)
		h = height / PathComputation.C_BESS_A

		rsinphi1 = (PathComputation.C_BESS_B / PathComputation.C_BESS_A) * math.sin(u) + h * math.sin(lat)
		rcosphi1 = math.cos(u) + h * math.cos(lat)

		# Step 2
		theta = GST - RA + lon

		sinD = math.sin(DE)
		cosD = math.cos(DE)

		X = rcosphi1 * math.sin(theta)
		Y = rsinphi1 * cosD - rcosphi1 * sinD * math.cos(theta)
		Z = rsinphi1 * sinD + rcosphi1 * cosD * math.cos(theta)

		return (X,Y,Z)


	def pathToKml(self) -> str:
		""" Exports the center line of the shadow to KML as a set of points """

		ret = ''

		# KML preamble (supports gx extensions)
		ret += '<?xml version="1.0" encoding="UTF-8"?>\r\n'
		ret += '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\r\n'

		# Track for path of occultation
		ret += '<Folder>\r\n'
		ret += '  <Placemark>\r\n'
		ret += '    <name>Track of center of asteroid shadow</name>\r\n'
		ret += '    <gx:Track>\r\n'
		ret += '    <altitudeMode>relativeToGround</altitudeMode>\r\n'

		# write out times of track points
		for epoch in self.centerPath['points']:
			ret += '      <when>%s</when>\r\n' % epoch[0].strftime('%Y-%m-%dT%H:%M:%SZ')

		# write out positions of track points
		for epoch in self.centerPath['points']:
			ret += '      <gx:coord>%0.6f %0.6f %0.6f</gx:coord>\r\n' % (epoch[2], epoch[1], 0.0)

		ret += '    </gx:Track>\r\n'
		ret += '  </Placemark>\r\n'
		ret += '</Folder>\r\n'

		# KML ending
		ret += '</kml>\r\n'

		return ret


occelmnt_test = { "Occultations": {
			"Event": {
				"Elements": "JPL#81:2023-07-30@2023-08-16[OWC],3.90,2023,8,16,8.706836,-0.330947,0.439776,-5.300154,-3.988511,-0.000865,-0.001414,0.000001,0.000000",
				"Earth": "-120.4068,0.7422,50.50,13.77,False",
				"Star": "TYC 559-01642-1,22.29196592,0.6233059,11.73,11.47,11.05,0.0,0,,22.31233020,0.7421805,1.82,1.80,0,0,0",
				"Object": "482,Petrina,13.07,45.8,1.8647,0,0,-1.667,-18.81,,2.4,0",
				"Orbit": "0,53.9673,2023,8,16,87.9178,179.3705,14.4736,0.09643,2.99829,2.70917,8.97,5.0,0.15",
				"Errors": "1.152,0.0107,0.0003,82,0.0052,Known errors,0.85,0,-1,-1",
				"ID": "20230816_1642-1,60157.39"
			}
		}
	}

def test_dateToGMST():
	pc =PathComputation(occelmnt_test)
	assert(pc.dateToGMST(datetime(2000,1,3,0,0,0,0)) == 1.7791727468540683)

def test_dateToGAST():
	pc =PathComputation(occelmnt_test)
	gast = pc.dateToGAST(datetime(2023,8,10,22,19,20,0))
	gast = math.degrees(gast) / 360.0 * 24.0
	assert(gast == 19.597849197665283)


def test_dateToEcliptic():
	pc =PathComputation(occelmnt_test)
	dToE = pc.dateToEcliptic(datetime(2023,8,10,3,35,11,00))
	assert(dToE == (0.4090392294437636, 3.903520318516651e-05, -3.3528985071917816e-05))

def test_dateToJD():
	pc = PathComputation(occelmnt_test)
	jd = pc.dateToJD(datetime(2023,8,10,22,19,20,0))
	assert( jd == 2460167.4300925927)

def test_centerOfAsteroidShadow1():
	pc = PathComputation(occelmnt_test, calcApparentStar=True)
	assert(pc.centerOfAsteroidShadow(datetime(2023, 8, 16, 8, 42, 24, 00)) == (26.953380941927033, -142.18636163089715))	#Center

def test_centerOfAsteroidShadow2():
	pc = PathComputation(occelmnt_test, calcApparentStar=True)
	assert(pc.centerOfAsteroidShadow(datetime(2023, 8, 16, 8, 25, 24, 00)) is None)

def test_centerOfAsteroidShadow3():
	pc = PathComputation(occelmnt_test, calcApparentStar=True)
	assert(pc.centerOfAsteroidShadow(datetime(2023, 8, 16, 8, 37, 46, 00)) == (49.44930320502795, -112.33891004640155))

def test_centerOfAsteroidShadow4():
	pc = PathComputation(occelmnt_test, calcApparentStar=False)
	assert(pc.centerOfAsteroidShadow(datetime(2023, 8, 16, 8, 37, 46, 00)) == (49.449455922244525, -112.33540415759194))

pc = PathComputation(occelmnt_test)
pc.timeAndChordDistanceForLocation(49.9925, -111.751944)
kmlStr = pc.pathToKml()
fp = open('test.kml', 'w')
fp.write(kmlStr)
fp.close()
