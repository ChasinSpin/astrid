# Reference: https://docs.astropy.org/en/latest/coordinates/satellites.html

import astropy
from astsite import AstSite
from astcoord import AstCoord
from astropy.time import Time
from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation, ITRS, AltAz, SkyCoord, ICRS
from astropy import units as u
from datetime import datetime
from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS


class Satellite:


	def __init__(self, name: str, tle: list, obstime: str):
		obstime = Time(datetime.strptime(obstime, '%Y-%m-%d %H:%M:%S.%f'), scale='utc', location = AstSite.location())

		# Calculate the velocity in kilometers and kilometers per second
		satellite = Satrec.twoline2rv(tle[0], tle[1])
		error_code, teme_p, teme_v = satellite.sgp4(obstime.jd1, obstime.jd2)	# in km and km/s
		if error_code != 0:
			raise RuntimeError(SGP4_ERRORS[error_code])
		print('teme_p:', teme_p)
		print('teme_v:', teme_v)

		# Create position in the TEME reference frame
		teme_p = CartesianRepresentation(teme_p * u.km)
		teme_v = CartesianDifferential(teme_v * u.km / u.s)
		teme = TEME(teme_p.with_differentials(teme_v), obstime = obstime)

		print('teme_p:', teme_p)
		print('teme_v:', teme_v)
		print ('teme:', teme)

		# Find the overhead latitude, longitude and height of the satellite
		itrs_geo = teme.transform_to(ITRS(obstime = obstime))
		earth_location = itrs_geo.earth_location
		print('Satellite current Geodetic position (Overhead latitude, longitude, height):', earth_location.geodetic)

		# Convert to AltAz Coordinates
		location = AstSite.location()
		topo_itrs_repr = itrs_geo.cartesian.without_differentials() - location.get_itrs(obstime).cartesian
		itrs_topo = ITRS(topo_itrs_repr, obstime = obstime, location = location)
		aa = itrs_topo.transform_to(AltAz(obstime = obstime, location = location))
		print('Altitude:', aa.alt)
		print('Azimuth:', aa.az)

		icrs = SkyCoord(alt = aa.alt, az = aa.az, obstime = obstime, frame='altaz', location=location).icrs
		coord = AstCoord.from360Deg(icrs.ra, icrs.dec, frame='icrs')
		print(coord)
		print(icrs)
		(ra, dec) = coord.raDec24Deg(frame='icrs', jnow = True, obsdatetime = obstime)
		print(ra)
		print(dec)

		(ra, dec) = coord.raDec360Deg(frame = 'icrs', jnow = False, obsdatetime = obstime)
		print('\t{')
		print('\t\t"name": "%s @ %s",' % (name, str(obstime)[11:]))
		print('\t\t"ra": %0.10f,' % (ra))
		print('\t\t"dec": %0.10f' % (dec))
		print('\t},')

		print('%s %s @ %s' % (name, coord.raDecHMSStr(frame='icrs', jnow = False, obsdatetime = obstime), obstime))

		self.alt = aa.alt
		self.az = aa.az
		self.ra = ra
		self.dec = dec
