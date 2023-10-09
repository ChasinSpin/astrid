import json
import pprint
import urllib.request, ssl
from settings import Settings



class OWCloud():

	URL_EVENTS_HOST = 'https://www.occultwatcher.net:443'
	URL_EVENTS_URL = '/api/v1/events/details-list'

	def __init__(self):
		observer = Settings.getInstance().observer
		self.__getUrl(OWCloud.URL_EVENTS_HOST, OWCloud.URL_EVENTS_URL)


	def __getUrl(self, host, url):
		observer = Settings.getInstance().observer

		# to avoid verifying ssl certificates
		httpsHa = urllib.request.HTTPSHandler(context= ssl._create_unverified_context())

		password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
		password_mgr.add_password(None, host, observer['owcloud_login'], observer['owcloud_password'], is_authenticated=True)

		handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
		opener = urllib.request.build_opener(handler, httpsHa)

		url = host + url
		response = opener.open(url)

		owevents = json.loads(response.read())

		print('Status: %d %s' % (response.status, response.reason))

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(owevents)
