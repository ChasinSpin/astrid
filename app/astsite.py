import astropy.units as u
from astropy.coordinates import EarthLocation
from astutils import AstUtils



class AstSite:
	lat		= 0.0	# Latitude degrees
	lon		= 0.0	# Longitude degrees
	alt		= 0.0	# Altitude meters
	pressure	= 0.0	# Pascals
	temperature	= 0.0	# Celcius
	rh		= 0.0	# 0 to 1.0

	@classmethod
	def set(cls, name: str, lat: float, lon: float, alt: float, pressure = 0.0, temperature = 15.0, rh = 0.5):
		cls.name	= name
		cls.lat		= lat
		cls.lon		= lon
		cls.alt		= alt
		cls.pressure	= pressure
		cls.temperature	= temperature
		cls.rh		= rh


	@classmethod
	def location(cls):
		return EarthLocation.from_geodetic(lon=cls.lon, lat=cls.lat, height=cls.alt*u.m)


	@classmethod
	def distanceFromGps(cls, gps_lat, gps_lon):
		""" Returns distance in meters between the site and GPS """
		return abs(AstUtils.haversineDistance(gps_lat, gps_lon, cls.lat, cls.lon))
