import numpy as np
from os import path as Path
import scipy.optimize
from datetime import datetime
import configparser
from astropy.coordinates import FK5, SkyCoord, AltAz
from functools import lru_cache
from astropy.wcs import WCS
from astropy.io import fits
from PlateSolver import *
from astsite import AstSite
from astcoord import AstCoord
import os


# References:
#
# Algorithm based on:
# 	Polar Align Algorithm:	https://tkarabela.github.io/posts/2021/understanding-photopolaralign.html
#	Code:			https://github.com/tkarabela/platesolve-polar-align
#
# All values "*_pix" are given in A local coordinates (ie. pixels)


class PolarAlignFile:
	def __init__(self, name: str):
		self.name = name


	def read_results(self):
		# Read WCS File
		self.wcs = None
		path = os.path.dirname(self.name) + '/astrometry_tmp/' + os.path.basename(self.name) + '.wcs'
		print("PolarAlignFile read_results wcs:", path)
		with open(path, "r", encoding="ascii", errors="ignore") as fp:
			self.wcs = fits.Header.fromstring(fp.read())

		# Read observation time from .fit file
		path = f"{self.name}.fit"
		print("PolarAlignFile read_results fit:", path)
		hdul = fits.open(path)
		timestamp_str = hdul[0].header['DATE-OBS']
		hdul.close()
		self.dateobs = datetime.fromisoformat(timestamp_str)


class PolarAlign:
	NCP_starting_ra		= 0.0
	NCP_starting_dec	= 90.0


	@lru_cache(maxsize=None)
	def __get_wcs(self, polarAlignFile):
		return WCS(self.__get_wcs_header(polarAlignFile))


	def __get_wcs_header(self, polarAlignFile):
		return polarAlignFile.wcs


	def __get_J2000(self, polarAlignFile) -> SkyCoord:
		h = self.__get_wcs_header(polarAlignFile)
		ra, dec = h["CRVAL1"], h["CRVAL2"]
		coord = SkyCoord(ra=ra, dec=dec, frame='fk5', unit="deg", equinox="J2000")
		return coord


	def __J2000_to_pix(self, polarAlignFile, coord: SkyCoord) -> np.ndarray:
		wcs = self.__get_wcs(polarAlignFile)
		return np.asarray(wcs.world_to_pixel(coord))


	def __pix_to_J2000(self, polarAlignFile: str, pix: np.ndarray) -> SkyCoord:
		x, y = pix
		wcs = self.__get_wcs(polarAlignFile)
		return wcs.pixel_to_world(x, y)


	def __get_time(self, polarAlignFile) -> datetime:
		return polarAlignFile.dateobs


	def __get_altaz_frame(self, polarAlignFile) -> AltAz:
		coord = self.__get_J2000(polarAlignFile)
		time = self.__get_time(polarAlignFile)
		altaz_frame = AltAz(obstime=time, location=AstSite.location())
		return altaz_frame


	def __get_altaz(self, polarAlignFile) -> SkyCoord:
		coord = self.__get_J2000(polarAlignFile)
		time = self.__get_time(polarAlignFile)
		altaz_frame = AltAz(obstime=time, location=AstSite.location())
		return coord.transform_to(altaz_frame)


	def __get_altaz_deg(self, polarAlignFile) -> np.ndarray:
		coord = self.__get_altaz(polarAlignFile)
		return np.asarray([coord.alt.deg, coord.az.deg])


	def __displacement_error_squared_time_comp(self, pix):
		coord_J2000_A = self.__pix_to_J2000(self.A, pix)
    
		if self.compensate_AB_time:
			# What we really want here is to project A(pix) -> Alt/Az -> B(pix2),
			# but platesolving gives us the projection in terms of Ra/Dec J2000.
			# Simply round-tripping through J2000 is not quite correct, since
			# A and B are taken at different times. (Imagine if the mount didn't
			# move at all between A and B - they would have same Alt/Az coordinates,
			# but sightly different J2000.) What we can do is to "fix" the J2000
			# coordinates, baking in the rotation due to time before looking them up in B.
			# Note that we rotate (ie. increment RA) around the CP to date, not the J2000 one.
			coord_to_date_A = coord_J2000_A.transform_to(FK5(equinox=self.A_time))
			coord_to_date_B = SkyCoord(ra=coord_to_date_A.ra.deg + 360 / 24 / 60 / 60 * self.dt_BA_sec,
						   dec=coord_to_date_A.dec.deg,  # ^ approx. 360?/day
						   frame='fk5', unit="deg", equinox=self.A_time)
			coord_J2000_B = coord_to_date_B.transform_to(FK5(equinox="J2000"))
		else:
			coord_J2000_B = coord_J2000_A
        
		pix2 = self.__J2000_to_pix(self.B, coord_J2000_B)
		return np.sum((pix - pix2) ** 2)


	def __init__(self, progress_callback):
		self.ncp_coord			= AstCoord.from360Deg(PolarAlign.NCP_starting_ra, PolarAlign.NCP_starting_dec, 'icrs')
		self.output_Ii_altaz_deg	= []
		self.output_Ri_altaz_deg	= []
		self.output_x_errors_arcmin	= []
		self.output_y_errors_arcmin	= []
		self.output_tot_errors_arcmin	= []
		self.output_xy_is_altaz		= True
		self.compensate_AB_time		= True  # <--- this should be True for best results

		self.progress_callback		= progress_callback


	def __solver_progress(self, msg):
		print(msg)
		self.progress_callback(msg)


	# Telescope in upright position (RA=0) and pointing approximately to the North Celestial Pole (NCP)
	# Take "A" Photo, Plate Solve and get details
	def step1(self, img, search_full_sky, callback):
		self.A		= PolarAlignFile(Path.splitext(img)[0])
		self.callback	= callback
		self.plateSolve = PlateSolver(self.A.name + '.fit', search_full_sky, self.__solver_progress, self.__step1_solved, self.__step1_failed, starting_coord=self.ncp_coord)
		return self.plateSolve


	def __step1_failed(self):
		self.callback(False, None)


	def __step1_solved(self, position, field_size, rotation_angle, index_file, focal_length, altAz):
		self.A.read_results()
		self.A_J2000		= self.__get_J2000(self.A)
		self.A_pix		= self.__J2000_to_pix(self.A, self.A_J2000)
		self.A_time		= self.__get_time(self.A)
		self.A_altaz_frame	= self.__get_altaz_frame(self.A)

		print("A_J2000:",	self.A_J2000)
		print("A_pix:",		self.A_pix)
		print("A_time:",	self.A_time)
		print("A_altaz_frame:",	self.A_altaz_frame)

		self.callback(True, position)


	# Rotate Scope in RA by about 90 degrees
	def step2(self, callback):
		print("Step2: Rotate RA 90 deg")
		callback(True, None)


	# Telescope in sideways position (RA=90)
	# Take "B" Photo, Plate Solve and get details
	def step3(self, img, search_full_sky, callback):
		self.B		= PolarAlignFile(Path.splitext(img)[0])
		self.callback	= callback
		self.plateSolve = PlateSolver(self.B.name + '.fit', search_full_sky, self.__solver_progress, self.__step3_solved, self.__step3_failed, starting_coord=self.ncp_coord)
		return self.plateSolve


	def __step3_failed(self):
		self.callback(False, None)

	
	def __step3_solved(self, position, field_size, rotation_angle, index_file, focal_length, altAz):
		self.B.read_results()
		self.B_J2000		= self.__get_J2000(self.B)
		self.B_pix		= self.__J2000_to_pix(self.A, self.B_J2000)
		self.B_altaz_frame	= self.__get_altaz_frame(self.B)
		self.B_altaz		= self.__get_altaz(self.B)
		self.B_altaz_deg	= self.__get_altaz_deg(self.B)
		self.B_time		= self.__get_time(self.B)

		print("B_J2000:",	self.B_J2000)
		print("B_pix:",		self.B_pix)
		print("B_time:",	self.B_time)
		print("B_altaz_frame:",	self.B_altaz_frame)
		print("B_altaz:",	self.B_altaz)
		print("B_altaz_deg:",	self.B_altaz_deg)

		self.dt_BA_sec = (self.B_time - self.A_time).total_seconds()

		res = scipy.optimize.minimize(self.__displacement_error_squared_time_comp, self.A_pix, method="nelder-mead")
		R0_pix = res.x
		R0_J2000 = self.__pix_to_J2000(self.A, R0_pix)
		R0_altaz = R0_J2000.transform_to(self.A_altaz_frame)
		self.R0_altaz_deg = np.asarray([R0_altaz.alt.deg, R0_altaz.az.deg])
		print("R_0:", R0_pix, R0_J2000, sep="\n", end="\n\n")

		NCP_J2000 = SkyCoord(ra=0, dec=90, frame='fk5', unit="deg", equinox="J2000")
		NCP_to_date_J2000 = SkyCoord(ra=0, dec=90, frame='fk5', unit="deg", equinox=self.__get_time(self.A)).transform_to(FK5(equinox="J2000"))
		NCP_to_date_pix = self.__J2000_to_pix(self.A, NCP_to_date_J2000)
		NCP_to_date_altaz = NCP_to_date_J2000.transform_to(self.A_altaz_frame)
		self.NCP_to_date_altaz_deg = np.asarray([NCP_to_date_altaz.alt.deg, NCP_to_date_altaz.az.deg])

		self.I = self.B
		self.__step4_solved(position, field_size, rotation_angle, index_file, focal_length, altAz)


	def step4(self, img, search_full_sky, callback):
		self.I		= PolarAlignFile(Path.splitext(img)[0])
		self.callback   = callback
		self.plateSolve = PlateSolver(self.I.name + '.fit', search_full_sky, self.__solver_progress, self.__step4_solved, self.__step4_failed, starting_coord=self.ncp_coord)

		return self.plateSolve


	def __step4_failed(self):
		self.callback(False, None)


	def __step4_solved(self, position, field_size, rotation_angle, index_file, focal_length, altAz):
		self.I.read_results()
		I_time		= self.__get_time(self.I)
		I_J2000		= self.__get_J2000(self.I)
		I_altaz		= self.__get_altaz(self.I)
		I_altaz_deg	= self.__get_altaz_deg(self.I)
		self.output_Ii_altaz_deg.append(I_altaz_deg)

		offset_altaz_deg = I_altaz_deg - self.B_altaz_deg
		Ri_altaz_deg = self.R0_altaz_deg + offset_altaz_deg
		self.output_Ri_altaz_deg.append(Ri_altaz_deg)

		p1 = SkyCoord(Ri_altaz_deg[1], Ri_altaz_deg[0], unit="deg")
		p2 = SkyCoord(self.NCP_to_date_altaz_deg[1], self.NCP_to_date_altaz_deg[0], unit="deg")
		error_deg = p1.separation(p2).deg
		error_az, error_alt = p2.spherical_offsets_to(p1)

		error_arcmin = error_deg * 60
		self.output_x_errors_arcmin.append(error_az.deg * 60)
		self.output_y_errors_arcmin.append(error_alt.deg * 60)
		self.output_tot_errors_arcmin.append(error_arcmin)

		print("X Error [arcmin]:", error_az.deg * 60)
		print("Y Error [arcmin]:", error_alt.deg * 60)

		print("Pointing To:", I_altaz_deg)
		print("Target:", Ri_altaz_deg)
		print("Pointing Error [arcmin]:", error_arcmin)
		correction = (-self.output_y_errors_arcmin[-1], -self.output_x_errors_arcmin[-1])
		print("Correction:", correction)
		instructions = "Instructions: Move Altitude: %0.4f %s   Azimuth: %0.4f %s   Pointing Error(arcmin): %0.4f" % (
					abs(correction[0]),
					"Down" if (correction[0] < 0) else "Up",
					abs(correction[1]),
					"West" if (correction[1] < 0) else "East",
					error_arcmin)
		print(instructions)
		self.progress_callback(instructions)

		self.callback(True, position, (correction[0]/60.0, correction[1]/60.0))
