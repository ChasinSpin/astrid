import math
import json
import psutil
import os, signal
from settings import Settings



class AstUtils:

	@classmethod
	def haversineDistance(cls, lat2: float, lon2: float, lat1: float, lon1: float) -> float:
		"""
		Calculates the distance in meters around the earth between 2 latitude/longitude pairs
		lat/lon are in degrees
		"""
		R = 6371000                     # metres
		u1 = math.radians(lat1)
		u2 = math.radians(lat2)
		mp = math.radians(lat2-lat1)
		dl = math.radians(lon2-lon1)

		a = math.sin(mp/2.0) * math.sin(mp/2.0) + math.cos(u1) * math.cos(u2) * math.sin(dl/2.0) * math.sin(dl/2.0)
		c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0-a))

		d = R * c

		return d


	@classmethod
	def read_file_as_string(cls,filename):
		# Opens filename and returns it's contents as a string
		f = open(filename, "r")
		data = f.read()
		f.close()

		return data


	@classmethod
	def stylesheetStrToColorScheme(cls, stylesheetStr):
		configs_fname = Settings.getInstance().configs_folder + '/configs.json'
		with open(configs_fname, 'r') as fp:
			configs = json.load(fp)

		colorSchemeName = configs['selectedColorScheme']

		with open('stylesheets/%s.colorscheme' % colorSchemeName) as f:
			cs = json.loads(f.read())

		# Do Macro search and replace
		for key in cs.keys():
			stylesheetStr = stylesheetStr.replace(key, cs[key])

		return stylesheetStr


	@classmethod
	def selectedConfigName(cls):
		configs_fname = Settings.getInstance().configs_folder + '/configs.json'
		with open(configs_fname, 'r') as fp:
			configs = json.load(fp)

		selectedIndex = configs['selectedIndex']
		return configs['configs'][selectedIndex]['summary']


	@classmethod
	def isProcessByNameRunning(cls, name: str) -> bool:
		process = list(filter(lambda p: p.name() == name, psutil.process_iter()))
		if len(process) > 0:
			return True
		return False


	@classmethod
	def killProcessesByName(cls, name: str):
		process = filter(lambda p: p.name() == name, psutil.process_iter())	
		for p in process:
			os.kill(p.pid, signal.SIGINT)

	
	@classmethod
	def setInternetPresent(cls, present: bool):
		cls.present = present


	@classmethod
	def isInternetPresent(cls) -> bool:
		return cls.present


	@classmethod
	def calculatePlateSolveTargetDelta(cls, plateSolveCoords, altAzPlateSolve, targetCoords):
		altAzTarget = targetCoords.altAzRefracted(frame='icrs')

		print('AltAzTarget:', altAzTarget)
		print('AltAzPlateSolve:', altAzPlateSolve)
		print('RaDecTarget:', targetCoords)
		print('RaDecPlateSolve:', plateSolveCoords)

		# Calculate delta
		#       Az: negative is rotate anti clockclockwise, positive is rotate clockwise
		#       Alt: negative is move down, positive is move up
		deltaAlt = altAzTarget[0] - altAzPlateSolve[0]
		deltaAz = altAzTarget[1] - altAzPlateSolve[1]

		# Calculate nearest azimuth direction if it's more than 180 degrees to the target
		if deltaAz > 180.0:
			deltaAz = -(360.0 - deltaAz)
		elif deltaAz < -180.0:
			deltaAz = -(-360.0 - deltaAz)

		# Calculate Ra/Dec delta in  360deg
		plateSolveRaDec	= plateSolveCoords.raDec360Deg(frame='icrs', jnow = True)
		targetRaDec	= targetCoords.raDec360Deg(frame='icrs', jnow = True)
		deltaRa		= targetRaDec[0] - plateSolveRaDec[0]
		deltaDec	= targetRaDec[1] - plateSolveRaDec[1]

		return ((deltaAlt, deltaAz), (deltaRa, deltaDec))
