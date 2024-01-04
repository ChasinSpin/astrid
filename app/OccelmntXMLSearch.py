import xmltodict
from PyQt5.QtCore import QDateTime
from datetime import datetime, timezone, timedelta
from pathcomputation import PathComputation
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astcoord import AstCoord
from astsite import AstSite



class OccelmntEvent():

	def __init__(self, object: str, eventTime: str, objectId: str, starId: str, duration: float, starMag: float, magDrop: float, starAlt: float, starDirection: str, sunAlt: float, pathWidthError: float, distance: float, occelmnt: dict):

		self.details = {						\
				'Object':		object,			\
				'Event Time':		eventTime,		\
				'#':			objectId,		\
				'Star Id':		starId,			\
				'Dur-s':		duration,		\
				'Dist km': 		distance,		\
				'MagV':			starMag, 		\
				'MagDrop':		magDrop,		\
				'Alt°':			starAlt,		\
				'Az':			starDirection,		\
				'SunAlt°':		sunAlt,			\
				'PathErr':		pathWidthError,		\
				}	

		if occelmnt is None:
			self.occelmnt = None
		else:
			occelmnt = xmltodict.unparse(occelmnt, pretty=True, full_document=False)
			self.occelmnt = '------ occelmnt file for Occult  BEGIN -----------------------------------\n' + occelmnt + '\n------ occelmnt file for Occult  END   -----------------------------------\n'


	def getValueForEvent(self, key):
		""" Returns value for key """
		if key == 'Event Time':
			return self.details[key].strftime('%Y-%m-%d %H:%M:%S')
		else:
			return self.details[key]


	def columns(self):
		return len(self.details.keys())


	def keys(self):
		return list(self.details.keys())



class OccelmntXMLSearch():

	def __init__(self, xml_fname):
		super().__init__()

		self.abort = False

		with open(xml_fname) as fd:
			self.events = xmltodict.parse(fd.read())['Occultations']['Event']

		self.total_events = len(self.events)
		self.found_events = []


	def __updateStatus(self, count, callback_status):
		callback_status('Analyzed %d of %d events (%0.1f%% complete) - found %d events' % (count, self.total_events, (float(count) / float(self.total_events)) * 100.0, len(self.found_events)))



	def __sunAltitude(self, lat, lon, altitude, obsdatetime):
		location 	= EarthLocation.from_geodetic(lon=lon, lat=lat, height=altitude*u.m)
		obstime		= Time(obsdatetime, scale='utc', location = location)
		coord		= AstCoord(get_sun(obstime))

		(alt, az) = coord.fastRaDecToAltAz(lat, lon, obsdatetime)

		#print('Sun: %s, %s' % (str(alt), str(az)))

		return alt


	def __starAltAz(self, ra, dec, lat, lon, obsdatetime):
		"""
			ra, dec are required to be apparent Ra/Dec
		"""
		coord = AstCoord.from24Deg(ra, dec, 'icrs')
		return coord.fastRaDecToAltAz(lat, lon, obsdatetime)


	def __azToCompass(self, az):
		if az > 337.5 or az <= 22.5:
			return 'N'
		elif az <= 67.5:
			return 'NE'
		elif az <= 112.5:
			return 'E'
		elif az <= 157.5:
			return 'SE'
		elif az <= 202.5:
			return 'S'
		elif az <= 247.5:
			return 'SW'
		elif az <= 292.5:
			return 'W'
		elif az <= 337.5:
			return 'NW'
		

	def searchEvents(self, lat, lon, alt, startDate, endDate, starMagLimit, magDropLimit, starAltLimit, sunAltLimit, distanceLimit, asteroidNum, callback_status, callback_foundEvent):
		count = 0

		for event in self.events:
			if self.abort:
				print('aborted...')
				return

			count 		+= 1
			if (count % 10) == 0:
				self.__updateStatus(count, callback_status)

			occElements	= event['Elements'].split(',')
			occStar		= event['Star'].split(',')
			occObject	= event['Object'].split(',')
			occErrors	= event['Errors'].split(',')

			occDateTime	= datetime(year=int(occElements[2]), month=int(occElements[3]), day=int(occElements[4]), tzinfo = timezone.utc) + timedelta(seconds=int(float(occElements[5]) * (60*60)))

			starMag		= round(float(occStar[4]), 1)
			magDrop		= round(float(occStar[11]), 1)

			# we cull in order of cpu time, cull the quick things first
			if asteroidNum != '' and asteroidNum is not None and occObject[0] != asteroidNum:
				continue
			if starMag > starMagLimit:
				continue
			if magDrop< magDropLimit:
				continue
			if occDateTime < startDate:
				continue
			if occDateTime > endDate:
				continue
			if self.__sunAltitude(lat, lon, alt, occDateTime) > sunAltLimit:
				continue

			(starAlt, starAz) = self.__starAltAz(float(occStar[9]), float(occStar[10]), lat, lon, occDateTime)
			#print('StarAzAlt %s %s   RA:%s DEC:%s' % (str(starAz), str(starAlt), occStar[9], occStar[10]))
			if starAlt < starAltLimit:
				continue

			wrapped_event		= {'Occultations': {'Event': event}}
			pathComp		= PathComputation(wrapped_event)
			timeAndChordForLoc	= pathComp.getTimeAndChordDistanceForLocation(lat, lon, alt)

			if timeAndChordForLoc is None:
				#print('No chord because star is not visible')
				pass
			else:
				pcTime = timeAndChordForLoc[0].replace(tzinfo = timezone.utc)
				pcDist = timeAndChordForLoc[1]

				distKm = round(pcDist / 1000.0, 2)
				if distKm < distanceLimit:
					eventTime	= pcTime.replace(microsecond=0) 

					objectName	= occObject[1]
					objectId	= int(occObject[0])
					starId		= occStar[0]
					duration	= round(float(occElements[1]), 1)
					pathWidthError	= round(float(occErrors[0]) - 1.0, 3)

					# Improve on the Sun and Star Altitudeby using the calculated event time now for the location
					sunAltitude = round(self.__sunAltitude(lat, lon, alt, eventTime), 0)
					(starAlt, starAz) = self.__starAltAz(float(occStar[9]), float(occStar[10]), lat, lon, eventTime)
					starAlt = round(starAlt, 0)

					starDirection = self.__azToCompass(starAz)

					oEvent = OccelmntEvent(object = objectName, eventTime = eventTime, objectId = objectId, starId = starId, duration = duration, starMag = starMag, magDrop = magDrop, starAlt = starAlt, starDirection = starDirection, sunAlt = sunAltitude, pathWidthError = pathWidthError, distance = distKm, occelmnt = wrapped_event)
					self.found_events.append(oEvent)
					#print('found event:', oEvent.details)

					self.__updateStatus(count, callback_status)
					callback_foundEvent(oEvent)
