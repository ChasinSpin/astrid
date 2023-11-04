import xmltodict
from PyQt5.QtCore import QDateTime
from datetime import datetime, timezone, timedelta
from pathcomputation import PathComputation
from astropy.time import Time
from astropy import units as u
from astropy.utils.iers.iers import conf
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astcoord import AstCoord
from astsite import AstSite



class OccelmntEvent():

	def __init__(self, object: str, eventTime: str, objectId: str, starId: str, duration: float, starMag: float, magDrop: float, pathWidthError: float, distance: float):
		self.details = {					\
				'Object': object,			\
				'Event Time': eventTime,		\
				'Object Id': objectId,			\
				'Star Id': starId,			\
				'Duration(s)': duration,		\
				'Star Mag.': starMag, 			\
				'Mag. Drop': magDrop,			\
				'Path Width Error': pathWidthError,	\
				'Distance(km)': distance		\
				}	


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



	def __sunAltitude(self, lat, lon, alt, obsdatetime):

		location 	= EarthLocation.from_geodetic(lon=lon, lat=lat, height=alt*u.m)
		obstime		= Time(obsdatetime, scale='utc', location = location)
		coord		= AstCoord(get_sun(obstime))

		# reference: https://stackoverflow.com/questions/60305302/converting-equatorial-to-alt-az-coordinates-is-very-slow
		conf.remote_timeout = 0.1
		conf.auto_download = False
		altaz = coord.skyCoord.transform_to(AltAz(obstime=obstime, location=location, pressure=AstSite.pressure*u.pascal, temperature=AstSite.temperature*u.Celsius, relative_humidity=AstSite.rh, obswl=0.65*u.micron))
		conf.remote_timeout = 10.0
		conf.auto_download = True

		return altaz.alt.deg
		

	def searchEvents(self, lat, lon, alt, startDate, endDate, starMagLimit, magDropLimit, callback_status, callback_foundEvent):
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

			starMag		= round(float(occStar[4]), 2)
			magDrop		= round(float(occStar[11]), 2)

			# we cull in order of cpu time, cull the quick things first
			if starMag > starMagLimit:
				continue
			if magDrop < magDropLimit:
				continue
			if occDateTime < startDate or occDateTime > endDate:
				continue
	

			wrapped_event		= {'Occultations': {'Event': event}}
			pathComp		= PathComputation(wrapped_event)
			timeAndChordForLoc      = pathComp.getTimeAndChordDistanceForLocation(lat, lon, alt)

			if timeAndChordForLoc is None:
				#print('No chord because star is not visible')
				pass
			else:
				distKm = round(timeAndChordForLoc[1] / 1000.0, 2)
				if distKm < 300:
					eventTime	= timeAndChordForLoc[0].replace(microsecond=0) 

					objectName	= occObject[1]
					objectId	= int(occObject[0])
					starId		= occStar[0]
					duration	= round(float(occElements[1]), 2)
					pathWidthError	= round(float(occErrors[0]) - 1.0, 3)

					oEvent = OccelmntEvent(object = objectName, eventTime = eventTime, objectId = objectId, starId = starId, duration = duration, starMag = starMag, magDrop = magDrop, pathWidthError = pathWidthError, distance = distKm)
					self.found_events.append(oEvent)
					print('found event:', oEvent.details)
					print('sun altitude:', self.__sunAltitude(lat, lon, alt, eventTime))

					self.__updateStatus(count, callback_status)
					callback_foundEvent(oEvent)
