import xmltodict
from datetime import datetime, timezone, timedelta
from pathcomputation import PathComputation



class OccelmntXMLSearch():

	def __init__(self, xml_fname):
		super().__init__()

		self.abort = False

		with open(xml_fname) as fd:
			self.events = xmltodict.parse(fd.read())['Occultations']['Event']

		self.total_events = len(self.events)
		


	def searchEvents(self, lat, lon, alt, callback_status):
		count = 0

		for event in self.events:
			if self.abort:
				print('Aborted...')
				return

			count 		+= 1
			if (count % 20) == 0:
				callback_status('Analyzed %d of %d events (%0.1f%% complete)' % (count, self.total_events, (float(count) / float(self.total_events)) * 100.0))

			occElements	= event['Elements'].split(',')
			occStar		= event['Star'].split(',')
			occObject	= event['Object'].split(',')
			occErrors	= event['Errors'].split(',')

			occDateTime	= datetime(year=int(occElements[2]), month=int(occElements[3]), day=int(occElements[4]), tzinfo = timezone.utc) + timedelta(seconds=int(float(occElements[5]) * (60*60)))

			wrapped_event		= {'Occultations': {'Event': event}}
			pathComp		= PathComputation(wrapped_event)
			timeAndChordForLoc      = pathComp.getTimeAndChordDistanceForLocation(lat, lon, alt)

			if timeAndChordForLoc is None:
				#print('No Chord because star is not visible')
				pass
			else:
				distKm = timeAndChordForLoc[1] / 1000.0
				if distKm < 300:
					print('time: %s id: %-6s name: %-14s star: %-16s duration: %-5s starmag: %-5s magdrop: %-5s pathwidtherr: %-7s dist: %0.4f km' % (str(timeAndChordForLoc[0]), occObject[0], occObject[1], occStar[0], occElements[1], occStar[4], occStar[11], '%0.3f' % (float(occErrors[0]) - 1.0), distKm))
					#print(event)
					#print(occDateTime)
		

		print('Searched: %d occultations' % len(self.events))
