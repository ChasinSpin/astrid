import sys
import math
from datetime import datetime, timedelta
from astcoord import AstCoord
from astutils import AstUtils



# Credit: Thanks to Steve Preston for these Occultation Path Calculations



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
	C_Mu = 0.2625161	# earth's rotation radians/hr

	def __init__(self, occelmnt: dict, useOccelmntApparentStarPosition = True):
		"""
		Given an occelmnt dictionary, it creates an object to calculate path information for the occultation
	
		useOccelmntApparentStarPosition:
			True  = use the apparent position for the star from the occelmnt
			False = calculate the apparent star position from the ICRS position in the occelmnt
		"""
	
		elements		= occelmnt['Occultations']['Event']['Elements'].split(',')
		star			= occelmnt['Occultations']['Event']['Star'].split(',')
		astobject		= occelmnt['Occultations']['Event']['Object'].split(',')

		self.XatClosest		= float(elements[6])
		self.YatClosest		= float(elements[7])
		self.dX			= float(elements[8])
		self.dY			= float(elements[9])
		self.d2X		= float(elements[10])
		self.d2Y		= float(elements[11])
		self.d3X		= float(elements[12])
		self.d3Y		= float(elements[13])
		self.astDiamKM      	= float(astobject[3])
	
		# Calculate Fractional hour of closest approach
		utcTime = elements[5]
		utcHour = int(utcTime.split('.')[0])
		utcFractionalHour = float(utcTime) - float(utcHour)
		utcHourSecs = utcFractionalHour * 3600
		utcMins = int(utcHourSecs / 60)
		utcSecs = int(utcHourSecs - (utcMins * 60))
		utcMicrosecs = int((utcHourSecs * 1000000.0) - (utcMins * 60 + utcSecs) * 1000000)

		self.dateTimeAtClosest = datetime(int(elements[2]), int(elements[3]), int(elements[4]), utcHour, utcMins, utcSecs, utcMicrosecs)
		#print("dateTimeAtClosest = ",self.dateTimeAtClosest)

		# calculate GAST at time of closest geocentric approach
		self.gstMid = self.dateToGAST(self.dateTimeAtClosest)

		# determine apparent position of star, note the result is a tuple (ra,dec) in 360deg
		if useOccelmntApparentStarPosition:
			self.apparentStarCoord	= ((float(star[9]) / 24.0) * 360.0, float(star[10]))
		else:
			self.apparentStarCoord = AstCoord.from24Deg(float(star[1]), float(star[2]),'icrs')
			self.apparentStarCoord = self.apparentStarCoord.raDec360DegTete(obsdatetime=self.dateTimeAtClosest)

		#print("ApparentStarCoord:", self.apparentStarCoord)

		#print("Closest Time:", self.dateTimeAtClosest)
		#print("Closest X:", self.XatClosest)
		#print("Closest Y:", self.YatClosest)

		#self.centerPath = self.__calcCenterPath(1.0)
		#print('Center path: start:%s end:%s # points:%d' % (str(self.centerPath['startDateTime']), str(self.centerPath['endDateTime']), len(self.centerPath['points'])))


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

		starRA = math.radians(self.apparentStarCoord[0])
		starDEC = math.radians(self.apparentStarCoord[1])

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


	def timeAndChordDistanceForLocationFP(self, lat: float, long: float, elev: float, toleranceKM = 0.1, maxRange = 2.0) -> (float, float):
		"""
		Inputs:
			lat,long,height = observer's lat, E long and elevation above ellipsoid (meters)
			toleranceKM = search tolerance in km
			maxRange = max geocentric range for search (earth equatorial radii units)

		Returns: tuple (minH, minDistanceKM)
			 dte = time of closest approach to observer (python datetime)
			 minDistanceKM = chord distance in fundamental plane at time of closest approach (km)

			OR returns None if no minimum found => star not visible from observer's location
		"""

		elev /= 1000.0	# Convert to KM

		# get apparent star coordinates
		starRA = math.radians(self.apparentStarCoord[0])
		starDEC = math.radians(self.apparentStarCoord[1])

		# lat,long in radians
		radLat = math.radians(lat)
		radLong = math.radians(long)

		# search tolerances
		#  
		toleranceER = toleranceKM / self.C_BESS_A
		speedKPH = math.sqrt( self.dX * self.dX + self.dY * self.dY) * self.C_BESS_A		# shadow speed in KM/Hour
		toleranceHR = toleranceKM / speedKPH												# time required for shadow traveling tolerance distance

		# initial search interval = time required for shadow traveling one asteroid diameter (hours)
		dHours = self.astDiamKM / speedKPH
		if (dHours < toleranceHR):
			dHours = toleranceHR		# search interval is minimum of tolerance and asteroid diameter

		# search forward in time from mid-time (time of closest geocentric approach)
		#  timeH = time offset (hrs) from the time of geocentric closest approach
		#  At each time step, compute the Fundamental Plane (FP) position of the projected location of the observer and the asteroid's shadow
		#    compute the distance between the FP position of the observer and shadow center, watch for the minimum distance
		#    exit this loop when the geocentric distance of the observer projected along the asteroid's motion is greater than maxRadius
		minDistance = None		# min distance from observer to asteroid shadow center
		minH = None			# time of min distance

		timeH = 0.0
		while True:
			theta = self.gstMid + timeH * self.C_Mu			# GAST at current time

			# compute FP position of observer at timeH
			(oX,oY,oZ) = self.bess_GeodeticToF(radLat,radLong,elev,starRA,starDEC,theta)

			# compute position of asteroid shadow center
			centerX = self.XatClosest + self.dX * timeH + self.d2X * timeH * timeH + self.d3X * timeH * timeH * timeH
			centerY = self.YatClosest + self.dY * timeH + self.d2Y * timeH * timeH + self.d3Y * timeH * timeH * timeH
			# compute asteroid motion vector
			motionX = self.dX + 2.0 * self.d2X * timeH + 3.0 * self.d3X * timeH * timeH
			motionY = self.dY + 2.0 * self.d2Y * timeH + 3.0 * self.d3Y * timeH * timeH
			# unit vector of motion
			motionTotal = math.sqrt( motionX * motionX + motionY * motionY)
			motionX = motionX / motionTotal
			motionY = motionY / motionTotal

			# check for end of search
			# dot product of Motion unit vector and Center position => offset of center position in direction of asteroid motion
			projectedCenter = motionX * centerX + motionY * centerY
			if (abs(projectedCenter) > maxRange):
				# projection of asteroid center is beyond the search distance from the geocenter => search is done
				break


			# search not finished, check the distance between the observer's FP position and the shadow center FP position
			# iff star is visible from observer's position, check distance to shadow in FP
			if oZ >= 0.0 :
				diffX = centerX - oX
				diffY = centerY - oY
				diffTotal = math.sqrt( diffX * diffX + diffY * diffY)
				if minDistance is None:
					minDistance = diffTotal
					minH = timeH
				elif (diffTotal < minDistance):
					minDistance = diffTotal
					minH = timeH

			# step forward in time
			timeH = timeH + dHours

		# search backward in time from mid-time
		# 
		timeH = -dHours
		while True:
			theta = self.gstMid + timeH * self.C_Mu			# GAST at current time

			# compute FP position of observer at timeH
			(oX,oY,oZ) = self.bess_GeodeticToF(radLat,radLong,elev,starRA,starDEC,theta)

			# compute position of asteroid shadow center
			centerX = self.XatClosest + self.dX * timeH + self.d2X * timeH * timeH + self.d3X * timeH * timeH * timeH
			centerY = self.YatClosest + self.dY * timeH + self.d2Y * timeH * timeH + self.d3Y * timeH * timeH * timeH
			# compute asteroid motion vector
			motionX = self.dX + 2.0 * self.d2X * timeH + 3.0 * self.d3X * timeH * timeH
			motionY = self.dY + 2.0 * self.d2Y * timeH + 3.0 * self.d3Y * timeH * timeH
			# unit vector of motion
			motionTotal = math.sqrt( motionX * motionX + motionY * motionY)
			motionX = motionX / motionTotal
			motionY = motionY / motionTotal

			# check for end of search
			# dot product of Motion unit vector and Center position => offset of center position in direction of asteroid motion
			projectedCenter = motionX * centerX + motionY * centerY
			if (abs(projectedCenter) > maxRange):
				# projection of asteroid center is beyond the search distance from the geocenter => search is done
				break

			# search not finished, check the distance between the observer's FP position and the shadow center FP position
			# if star is visible from observer's position, check distance to shadow in FP
			if oZ >= 0.0 :
				diffX = centerX - oX
				diffY = centerY - oY
				diffTotal = math.sqrt( diffX * diffX + diffY * diffY)
				if minDistance is None:
					minDistance = diffTotal
					minH = timeH
				elif (diffTotal < minDistance):
					minDistance = diffTotal
					minH = timeH

			# step backward in time
			timeH = timeH - dHours

		# check for no minimum => star not visible from observer's location
		#  return None
		if (minDistance is None):
			return None
		
		# final search to ensure that we meet the desired tolerance
		#
		if (toleranceHR < dHours):
			startH = minH - dHours
			endH = minH + dHours
			dHours = toleranceHR		# tolerance in hours is now our step size

			timeH = startH
			while (timeH <= endH):
				theta = self.gstMid + timeH * self.C_Mu			# GAST at current time

				# compute FP position of observer at timeH
				(oX,oY,oZ) = self.bess_GeodeticToF(radLat,radLong,elev,starRA,starDEC,theta)

				# if star is visible from observer's position, check distance to shadow in FP
				if oZ >= 0.0 :
					# compute position of asteroid shadow center
					centerX = self.XatClosest + self.dX * timeH + self.d2X * timeH * timeH + self.d3X * timeH * timeH * timeH
					centerY = self.YatClosest + self.dY * timeH + self.d2Y * timeH * timeH + self.d3Y * timeH * timeH * timeH

					# compute asteroid motion vector
					motionX = self.dX + 2.0 * self.d2X * timeH + 3.0 * self.d3X * timeH * timeH
					motionY = self.dY + 2.0 * self.d2Y * timeH + 3.0 * self.d3Y * timeH * timeH
					# unit vector of motion
					motionTotal = math.sqrt( motionX * motionX + motionY * motionY)
					motionX = motionX / motionTotal
					motionY = motionY / motionTotal

					# check the distance between the observer's FP position and the shadow center FP position
					diffX = centerX - oX
					diffY = centerY - oY
					diffTotal = math.sqrt( diffX * diffX + diffY * diffY)
					if (diffTotal < minDistance):
						minDistance = diffTotal
						minCenterXY = (centerX, centerY)
						minMotionXY = (motionX, motionY)
						minH = timeH

				# step forward in time
				timeH = timeH + dHours

		dteMin = self.dateTimeAtClosest + timedelta(hours=minH)

		"""

		DISABLED FOR NOW
		# Calculate the extent of the shadow
		#	minCenterXY is the position on the fundamental plane of the center of the asteroid shadow at minDistance
		#	minMotionXY is the unit vector for the direction of motion along the fundamental plane at minDistance
		#
		#print('Min Motion XY:', minMotionXY)
		#print('Min Center XY:', minCenterXY)

		astRadiusFP		= (self.astDiamKM / self.C_BESS_A) / 2.0 						# Convert the asteroid diameter (in km's) into the radius in the unit (-1 to 1) fundamental plane
		scaledMotionVector	= (astRadiusFP * minMotionXY[0], astRadiusFP * minMotionXY[1])				# Scale the motion vector to the asteroid radius
		#print('ScaledMotionVector:', scaledMotionVector)
		shadowExtentXY		= (minCenterXY[0] + scaledMotionVector[0], minCenterXY[1] + scaledMotionVector[1])	# Extend the asteroid radius in the direction of motion (unit vector) along the asteroid center line
		#print('ShadowExtentXY:', shadowExtentXY)

		# Rotate shadowExtentXY around minCenterXY by -90 and 90 deg (perpendicular) to get the extent of the path in the fundemantal plane
		limitPath1 = self.__rotatePointAboutCenter(shadowExtentXY, minCenterXY, 90)
		limitPath2 = self.__rotatePointAboutCenter(shadowExtentXY, minCenterXY, -90)
		#print('Limit Path1:', limitPath1)
		#print('Limit Path2:', limitPath2)

		# At this point, minCenterXY is the center location and limitPath1, limitPath2 are 2 points perpendicular to the motion of the asteroid, 1 diameter apart (all in the fundamental plane)
		# Now project these points onto the earth's surface
		gastEventTime = self.dateToGMST(dteMin)

		latlon1 = self.bess_FtoGeodetic(limitPath1[0], limitPath1[1], starRA, starDEC, gastEventTime)
		latlon2 = self.bess_FtoGeodetic(limitPath2[0], limitPath2[1], starRA, starDEC, gastEventTime)

		# Convert latlon from radians to degrees
		if latlon1 is not None:
			latlon1 = (math.degrees(latlon1[0]), math.degrees(latlon1[1]))
		if latlon2 is not None:
			latlon2 = (math.degrees(latlon2[0]), math.degrees(latlon2[1]))

		print('LatLon1:', latlon1)
		print('LatLon2:', latlon2)

		print('CenterOfAsteroidShadow:', self.centerOfAsteroidShadow(dteMin))
		"""

		# return time and distance of closest approach
		return ( dteMin, minDistance * self.C_BESS_A )


	def __rotatePointAboutCenter(self, point, center, rotation):
		""" Rotates point(x,y) about center(x,y) by rotation degrees """
		theta	= math.radians(rotation)
		p	= (point[0] - center[0], point[1] - center[1])								# Translate to origin
		p	= (p[0] * math.cos(theta) - p[1] * math.sin(theta), p[1] * math.cos(theta) - p[0] * math.sin(theta))	# Rotate
		p	= (p[0] + center[0], p[1] + center[1])									# Translate back
		return p


	def dateToGAST(self, dteDate: datetime) -> float:
		"""
		Calculates Greenwich Apparent Sideral Time (GAST) in radians for a given utc date/time
			dteDate = datetime utc
			Returns: GAST in radians
		"""
		GMST = self.dateToGMST(dteDate)
		self.midGMST = GMST

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


	def bess_GeodeticToF(self, lat: float, lon: float, height: float, RA: float, DE: float, GST: float) -> (float, float, float):
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


	def getTimeAndChordDistanceForLocation(self, lat: float, lon: float, alt: float):
		"""
			Given a latitude, longitude and altitude, calculates the chord distance and the center time of the event at that location

			Parameters:
				lat:	latitude
				lon: 	longitude
				alt:	altitude (meters)

			Returns:
				Tuple (datetime, chord_distance(meters))
				or None if the star is not visible from the location
		"""
		minApproach = self.timeAndChordDistanceForLocationFP(lat, lon, alt)
		if minApproach is None:
			return None
	
		dteMin		= minApproach[0]
		minChord	= minApproach[1]
		return (dteMin, minChord * 1000.0)


#pc = PathComputation(occelmnt_test)
#timeAndChordForLoc = pc.getTimeAndChordDistanceForLocation(51.0000, -110.000000, 1000.0)
#if timeAndChordForLoc is None:
#	print('Error: Star not visible from this location.')
#else:
#	print('Time: %s Distance: %0.4f km' % (str(timeAndChordForLoc[0]), timeAndChordForLoc[1] / 1000.0) )
