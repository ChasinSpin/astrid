from processlogger import ProcessLogger
import math
import json
import pprint
import binascii
import urllib.request, ssl
from settings import Settings
from datetime import datetime, timedelta



class OWCloud():

	URL_EVENTS_HOST		= 'https://www.occultwatcher.net:443'
	URL_EVENTS_ENDPOINT	= '/api2/v1/events/details-list'
	URL_OCCELMNT_ENDPOINT	= '/api2/v1/owc/event/my/%s/occelmnts'
	API_KEY			= b'6266393530376536666264303434623138383963653339396636396366613663'

	MOON_MULTIPLIER = 10.0  # Multiplier for detecting moons, this gets multiplied by the event duration


	def __init__(self):
		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()
		observer = Settings.getInstance().observer


	def __getUrl(self, host, url, apiKey):
		observer = Settings.getInstance().observer

		# to avoid verifying ssl certificates
		httpsHa = urllib.request.HTTPSHandler(context= ssl._create_unverified_context())

		password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
		password_mgr.add_password(None, host, observer['owcloud_login'], observer['owcloud_password'], is_authenticated=True)

		handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
		opener = urllib.request.build_opener(handler, httpsHa)

		if '?' in url:
			sep = '&'
		else:
			sep = '?'
		url = host + url + sep + 'apikey=%s' % binascii.unhexlify(apiKey).decode('ascii')

		try:
			response = opener.open(url, timeout=5)
		except Exception as error:
			self.logger.error('Unable to download OWCloud data: %s' % str(error))
			return (None, str(error))
		else:
			self.logger.info('OWCloud Status: %d %s' % (response.status, response.reason))
			if response.status == 200:
				owevents = json.loads(response.read())

				pp = pprint.PrettyPrinter(indent=4)
				pp.pprint(owevents)

				return (owevents, None)
			else:
				return (None, 'Response status != 200: %d' % response.status)
				

	def getEvents(self):
		"""
			Returns:
				Tuple (owevents, error)

				Where:
					owevents = the list of events from OWCloud, None if there was an error
					error = None is there was no error, otherwise a textual representation of the error
		"""
		
		(owevents, error) = self.__getUrl(OWCloud.URL_EVENTS_HOST, OWCloud.URL_EVENTS_ENDPOINT, OWCloud.API_KEY)
		if error is not None or owevents is None:
			return (owevents, error)

		occultations = []
		for owevent in owevents:
			name            = owevent['Object']
			eventDuration   = owevent['MaxDurSec']
			eventId		= owevent['Id']

			for station in owevent['Stations']:
				if station['IsOwnStation']:
					eventTime               = station['EventTimeUtc']
					eventUncertainty        = station['ErrorInTimeSec']
					stationName             = station['StationName']

					extraSecs               = int(math.ceil(eventDuration * OWCloud.MOON_MULTIPLIER))
					extraStartSecs          = extraSecs
					extraEndSecs            = extraSecs

					eventCenterTime = datetime.strptime(eventTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')

					# Calculate the Start/End Times
					startTime = eventCenterTime
					startTime -= timedelta(seconds = eventDuration / 2.0)
					startTime -= timedelta(seconds = eventUncertainty)
					startTime -= timedelta(seconds = extraStartSecs)

					endTime = eventCenterTime
					endTime += timedelta(seconds = eventDuration / 2.0)
					endTime += timedelta(seconds = eventUncertainty)
					endTime += timedelta(seconds = extraEndSecs)

					eventCenterTime = eventCenterTime.strftime("%Y-%m-%dT%H:%M:%S")
					startTime       = startTime.strftime("%Y-%m-%dT%H:%M:%S")
					endTime         = endTime.strftime("%Y-%m-%dT%H:%M:%S")

					# Get the occelmnt
					occelmntUrl = OWCloud.URL_OCCELMNT_ENDPOINT % eventId
					(eventOccelmnt, error) = self.__getUrl(OWCloud.URL_EVENTS_HOST, occelmntUrl, OWCloud.API_KEY)

					if error is not None or eventOccelmnt is None:
						return (eventOccelmnt, error)

					elements	= eventOccelmnt['Occultations']['Event']['Elements'].split(',')
					star		= eventOccelmnt['Occultations']['Event']['Star'].split(',')
					object		= eventOccelmnt['Occultations']['Event']['Object'].split(',')
					owcloudurl	= 'https://cloud.occultwatcher.net' +  eventOccelmnt['Occultations']['Event']['OWC']
					ra		= (float(star[1]) / 24.0) * 360.0
					dec		= float(star[2])

					occultation = { 'name': name + ' - ' + stationName, 'ra': ra, 'dec': dec, 'event_time': eventCenterTime, 'start_time': startTime, 'end_time': endTime, 'event_duration': eventDuration, 'event_uncertainty': eventUncertainty, 'occelmnt': eventOccelmnt, 'source': 'OWCloud' }
					if owcloudurl is not None:
						occultation['owcloudurl'] = owcloudurl

					# Add the occultation
					occultations.append(occultation)

		return (occultations, None)
