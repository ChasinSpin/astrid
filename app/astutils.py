import math



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
