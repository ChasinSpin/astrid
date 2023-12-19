import os
import subprocess
import shlex
from astropy.io import fits
from settings import Settings
from astcoord import AstCoord
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from AstrometryDownload import AstrometryDownload
from UiPanelAstrometry import UiPanelAstrometry
from UiDialogPanel import UiDialogPanel


# Plate solver uses ICRS coordinates, but internally uses FK5

class PlateSolverThread(QThread):
	finished = pyqtSignal(bool)
	progress = pyqtSignal(str)

	def __init__(self, filename, scale_low, scale_high, starting_ra, starting_dec, starting_radius, limit_objs, downsample, source_extractor, obsdatetime, configFile):
		super(QThread, self).__init__()
		self.filename		= filename
		self.scale_low		= scale_low
		self.scale_high		= scale_high
		self.starting_ra	= starting_ra
		self.starting_dec	= starting_dec
		self.starting_radius	= starting_radius
		self.limit_objs		= limit_objs
		self.downsample		= downsample
		self.source_extractor	= source_extractor
		self.obsdatetime	= obsdatetime
		self.configFile		= configFile
		self.altAz		= None


	def run(self):
		self.progress.emit("Plate solving...")

		astrometry_output = os.path.dirname(self.filename) + '/astrometry_tmp'

		cmd = ["/usr/bin/solve-field",
			"--config", self.configFile,
			"--dir", astrometry_output,
			#"--corr", "astrometry.corr",
			"--overwrite",
			"--scale-low", str(self.scale_low),
			"--scale-high", str(self.scale_high),
			"--scale-units", "degwidth",
			"--objs", str(self.limit_objs),
			"--downsample", str(self.downsample),
			"--no-plots",
			"--tweak-order", "2",

			# "-L", "0.3",
			# "--sigma", "35.0",
			# "--sigma", "50.0",
			# "-d", "10",

			"--crpix-center"]

		if self.source_extractor:
			cmd.append("--use-source-extractor")	# Use Source Extractor instead of simplexy algorithm to detect stars

		# Add a starting ra/dec if we have one
		if self.starting_ra is not None and self.starting_dec is not None:
			cmd.append("--ra");	cmd.append(str(self.starting_ra))
			cmd.append("--dec");	cmd.append(str(self.starting_dec))
			if self.starting_radius is not None:
				cmd.append("--radius");	cmd.append(str(self.starting_radius))		# Only search in a radius of this many degrees from ra/dec


		cmd.append(self.filename)

		print("Command:", cmd)

		self.process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)

		sources = ""
		location = ""
		self.decimal_location = ""
		self.field_size = ""
		self.rotation_angle = ""
		self.index_file = ""
		success = False

		while True:
			output = self.process.stdout.readline()
			if output == '' or self.process.poll() is not None:
				break
			if output:
				soutput = output.decode('ascii')
				soutput_stripped = soutput.strip()
				print(soutput_stripped)
				if "simplexy:" in soutput:
					sources = soutput.replace("simplexy: found ","").replace(".","")
				if "Field center: (RA H:M:S, Dec D:M:S) = (" in soutput:
					location = soutput.replace("Field center: (RA H:M:S, Dec D:M:S) = (", "")
					location = location.replace(").","")
					location = location.split(", ")
					location = "Solved RA:%s Dec:%s" % (location[0], location[1])	 # Note this is just textual information and is FK5 J2000
					success = True
				if "Field center: (RA,Dec) = (" in soutput:
					self.decimal_location = soutput.replace("Field center: (RA,Dec) = (", "")
					self.decimal_location = self.decimal_location.replace(") deg.\n","")
					self.decimal_location = self.decimal_location.split(", ")
					self.icrs_coords = AstCoord.from360Deg(float(self.decimal_location[0]), float(self.decimal_location[1]), 'fk5')
				if "Did not solve (or no WCS file was written)." in soutput:
					location = "Failed to Plate Solve"
				if "Field size: " in soutput_stripped:
					self.field_size = soutput_stripped.replace("Field size: ", "")
					self.field_size = self.field_size.replace(' x ', ',')

					print('<%s>' % (self.field_size))
					if self.field_size.endswith(' arcminutes'):
						self.field_size = self.field_size.replace(' arcminutes', '')
						print('<%s>' % (self.field_size))
						self.field_size = self.field_size.split(',')
						self.field_size = (float(self.field_size[0]), float(self.field_size[1]))
						self.field_size = (self.field_size[0] / 60.0, self.field_size[1] / 60.0)
						self.field_size = '%0.3fx%0.3f°' % (self.field_size[0], self.field_size[1])
					if self.field_size.endswith(' arcdegrees'):
						self.field_size = self.field_size.replace(' arcdegrees', '')
						self.field_size = self.field_size.split(',')
						self.field_size = (float(self.field_size[0]), float(self.field_size[1]))
						self.field_size = (self.field_size[0] / 3600.0, self.field_size[1] / 3600.0)
						self.field_size = '%0.3fx%0.3f°' % (self.field_size[0], self.field_size[1])
					if self.field_size.endswith(' degrees'):
						self.field_size = self.field_size.replace(' degrees', '')
						self.field_size = self.field_size.split(',')
						self.field_size = (float(self.field_size[0]), float(self.field_size[1]))
						self.field_size = '%0.3fx%0.3f°' % (self.field_size[0], self.field_size[1])
				if "Field rotation angle: " in soutput_stripped:
					self.rotation_angle = soutput_stripped.replace("Field rotation angle: ", "")
					self.rotation_angle = self.rotation_angle.replace('degrees', '°')
					self.rotation_angle = self.rotation_angle.replace("up is ", "")
				if "Field 1: solved with index " in soutput_stripped:
					self.index_file = soutput_stripped.replace("Field 1: solved with index ","")
					self.index_file = self.index_file.replace(".fits.","")
					self.index_file = self.index_file.replace(".littleendian","")
	
				if soutput_stripped != 'Done':
					self.progress.emit('Plate Solver Log: ' + soutput_stripped)

		rc = self.process.poll()

		if success:
			self.altAz = self.icrs_coords.altAzRefracted('icrs', obsdatetime=self.obsdatetime)
			location += " (Azimuth:%0.3f Altitude:%0.3f)" % (self.altAz[1], self.altAz[0])

		self.progress.emit("%s" % (location))

		'''
			Example output:

			Reading input file 1 of 1: "Light/M51_0083.fit"...
			Extracting sources...
			Downsampling by 2...
			simplexy: found 412 sources.
			Solving...
			Reading file "Light/M51_0083.axy"...
			Field 1 did not solve (index index-tycho2-12.littleendian.fits, field objects 1-10).
			Field 1 did not solve (index index-tycho2-11.littleendian.fits, field objects 1-10).
			Field 1 did not solve (index index-tycho2-10.littleendian.fits, field objects 1-10).
			  log-odds ratio 159.624 (2.10823e+69), 17 match, 0 conflict, 42 distractors, 21 index.
			  RA,Dec = (210.924,54.5265), pixel scale 0.918334 arcsec/pix.
			  Hit/miss:   Hit/miss: ++++-++++---+++--+--++------+-------+---------------------+(best)-------------------------------------++++
			Field 1: solved with index index-tycho2-09.littleendian.fits.
			Field 1 solved: writing to file Light/M51_0083.solved to indicate this.
			Field: Light/M51_0083.fit
			Field center: (RA,Dec) = (210.923828, 54.526420) deg.
			Field center: (RA H:M:S, Dec D:M:S) = (14:03:41.719, +54:31:35.110).
			Field size: 62.0638 x 46.5507 arcminutes
			Field rotation angle: up is 91.852 degrees E of N
			Field parity: neg
			Creating new FITS file "Light/M51_0083.new"...
				
			OR
				
			Did not solve (or no WCS file was written).
		'''

		self.finished.emit(success)


	def terminator(self):
		subprocess.Popen.kill(self.process)


class PlateSolver:

	# search_full_sky	set to true to search the whole sky rather than just with search_radius_deg
	# progress_callback takes a string
	# finished_callback is called at the end
	# starting_coord	the starting RA/DEC location for the search in icrs format, if set to None it's obtained from the fits
	# It's important to keep a reference to this object, otherwise the thread will be garbage collected and killed

	def __init__(self, filename, search_full_sky, progress_callback, success_callback, failure_callback, starting_coord = None):

		self.settings = Settings.getInstance().platesolver

		# Read fits header
		hdul = fits.open(filename)
		hdr = hdul[0].header
		self.frame_width_mm = hdr['NAXIS1'] * (hdr['XPIXSZ']/1000.0)
		self.obsdatetime = hdr['DATE-OBS']

		# Calculate FOV
		if 'FOCALLEN' in hdr.keys():
			self.focalLen = hdr['FOCALLEN']
		else:
			self.focalLen = Settings.getInstance().platesolver['focal_length']

		fov = (57.3 / self.focalLen) * self.frame_width_mm
		print("Sensor FOV: %f deg" % (fov))
		scale_low = fov * self.settings['scale_low_factor']
		scale_high = fov * self.settings['scale_high_factor']

		print("Plate Solving: Frame_Width(mm):", self.frame_width_mm)

		# Check we have the astrometry files we need, and download if we don't
		astrometryDownload = AstrometryDownload(astrid_drive = Settings.getInstance().astrid_drive, focal_length = self.focalLen, frame_width_mm = self.frame_width_mm)
		if not astrometryDownload.astrometryFilesArePresent():
			dialog = UiDialogPanel('Astrometry Download', UiPanelAstrometry, args = astrometryDownload)
		astrometryCfg = astrometryDownload.generateAstrometryCfg()
		astrometryDownload = None

		if search_full_sky:
			# Don't use starting_coord, search the whole sky
			starting_radius = None
			starting_ra = None
			starting_dec = None
		else:
			if starting_coord is None:
				# Obtain starting_coord from fits file
				if 'RA' in hdr and 'DEC' in hdr:
					(starting_ra, starting_dec) = (hdr['RA'], hdr['DEC'])
				else:
					# If there's no RA/DEC in the header file, then search the whole sky
					search_full_sky = True
					starting_radius = None
					starting_ra = None
					starting_dec = None
			else:
				# Use starting_coord
				(starting_ra, starting_dec) = starting_coord.raDec360Deg('fk5')

			starting_radius = self.settings['search_radius_deg']

		hdul.close()

		print("Plate Solving from: (%s,%s,%s)" % (starting_ra, starting_dec, starting_radius))

		self.progress_callback	= progress_callback
		self.success_callback	= success_callback
		self.failure_callback	= failure_callback

		self.thread = PlateSolverThread(filename, scale_low, scale_high, starting_ra, starting_dec, starting_radius, self.settings['limit_objs'], self.settings['downsample'], self.settings['source_extractor'], self.obsdatetime, astrometryCfg)
		self.thread.progress.connect(self.__progress)
		self.thread.finished.connect(self.__finished)
		#self.thread.finished.connect(self.thread.deleteLater)
		self.thread.start()


	def __progress(self, txt):
		self.progress_callback(txt)


	def __finished(self, success):
		if success:
			# Figure out focal length
			(fov_width, _) = self.thread.field_size.split('x')
			fov_width = float(fov_width)
			focal_length = 57.3 / (fov_width / self.frame_width_mm)
			print('Plate Solver Success: Pos:%s FOV:%s Rot:%s Index:%s FL:%fmm' % (self.thread.icrs_coords.raDecHMSStr('icrs'), self.thread.field_size, self.thread.rotation_angle, self.thread.index_file, focal_length))
			self.success_callback(self.thread.icrs_coords, self.thread.field_size, self.thread.rotation_angle, self.thread.index_file, focal_length, self.thread.altAz)
		else:
			self.failure_callback()

		self.thread.wait()
		self.thread = None	# Allow garbage collection


	def cancel(self):
		if self.thread is not None:
			self.thread.terminator()
			self.thread.wait()
