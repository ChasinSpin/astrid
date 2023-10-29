from processlogger import ProcessLogger
import json
import pprint
import urllib.request, ssl
from settings import Settings




class OWCloud():

	URL_EVENTS_HOST = 'https://www.occultwatcher.net:443'
	URL_EVENTS_URL = '/api/v1/events/details-list'

	def __init__(self):
		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()
		observer = Settings.getInstance().observer


	def __getUrl(self, host, url):
		observer = Settings.getInstance().observer

		# to avoid verifying ssl certificates
		httpsHa = urllib.request.HTTPSHandler(context= ssl._create_unverified_context())

		password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
		password_mgr.add_password(None, host, observer['owcloud_login'], observer['owcloud_password'], is_authenticated=True)

		handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
		opener = urllib.request.build_opener(handler, httpsHa)

		url = host + url

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
					owevents = the list of events from OWCloud, None is there was an error
					error = None is there was no error, otherwise a textual representation of the error
		"""
		
		return self.__getUrl(OWCloud.URL_EVENTS_HOST, OWCloud.URL_EVENTS_URL)
