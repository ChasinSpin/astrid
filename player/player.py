#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess
#import numpy as np
from astropy.io import fits

sys.path.append('../app')

import cv2
import numpy as np
from UiPlayer import UiPlayer
from astutils import AstUtils
from UiDialogPanel import UiDialogPanel
from UiPanelMessage import UiPanelMessage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from ravf import RavfReader, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox, RavfImageUtils
from FileHandling import *
from astcoord import AstCoord
from datetime import timedelta, timezone
from PlateSolver import PlateSolver
from settings import Settings


# Export Fits Sequence on a separate thread

class ExportFitsSequenceThread(QThread):
	exportFitsSequenceStatus	= pyqtSignal(str)
	exportFitsSequenceFinished	= pyqtSignal()


	def __init__(self):
		super(QThread, self).__init__()
		self.terminate_now = False


	def run(self):
		f_basename = os.path.splitext(ravf_filename)[0]
		f_dir, f_fnamestem = os.path.split(f_basename)

		f_seqfolder = f_basename + '_fits_seq'

		try:
			os.mkdir(f_seqfolder)
		except FileExistsError:
			print('%s already exists' % f_seqfolder)
			pass

		frameFirst()
		for i in range(ravf.frame_count()):
			if self.terminate_now:
				break

			img_filename = '%s/%s_%06d.fits' % (f_seqfolder, f_fnamestem, current_frame)
			self.exportFitsSequenceStatus.emit('Exporting: ' + img_filename)

			start_timestamp = frameStatus['start_timestamp']
			epoch = datetime(2010, 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo = timezone.utc) # 00:00:00 1st Jan 2010
			frame_seconds_since_epoch = timedelta(seconds = start_timestamp / 1000000000)
			obsDateTime = epoch + frame_seconds_since_epoch
			#print(obsDateTime)
			expTime = frameStatus['exposure_duration'] / 1000000000.0
	
			save_fits_frame(lastImage, img_filename, obsDateTime, expTime, current_frame)
			print(img_filename)
			frameNext()
		
		if self.terminate_now:
			self.exportFitsSequenceStatus.emit('Aborting fits sequence export, export incomplete!')
		else:
			self.exportFitsSequenceStatus.emit('Finished exporting fits sequence')

		self.exportFitsSequenceFinished.emit()


def closeRavf():
	global ravf_fp, ravf
	if ravf_fp is not None:
		ravf_fp.close() 
		ravf = None
		ravf_fp = None


def drawTarget(img, centerGap, lineLength, lineThickness, pos, colors):
	x = pos[0]
	y = pos[1]

	for colorThickness in [[colors[0], lineThickness*3], [colors[1], lineThickness]]:
		color		= colorThickness[0]
		thickness	= colorThickness[1]

		cv2.line(img, (x, y-centerGap), (x, y-lineLength), (color), thickness)
		cv2.line(img, (x, y+centerGap), (x, y+lineLength), (color), thickness)
		cv2.line(img, (x-centerGap, y), (x-lineLength, y), (color), thickness)
		cv2.line(img, (x+centerGap, y), (x+lineLength, y), (color), thickness)


def getRavfFrame(index):
	global ravf_fp, ravf, window, width, height, autoStretch, autoStretchLower, autoStretchUpper, targetPosition, lastDisplayImage, lastImage, frameInfo, frameStatus

	if ravf_fp is None or ravf is None:
		return

	(err, lastImage, frameInfo, frameStatus) = ravf.getPymovieMainImageAndStatusData(ravf_fp, index)

	if err:
		raise ValueError('error reading frame: %d', index)

	#print(lastImage.shape)

	if targetPosition is not None:
		scaledTargetPosition = (targetPosition[0] * (width/lastImage.shape[1]), targetPosition[1] * (height/lastImage.shape[0]))
		scaledTargetPosition = (int(scaledTargetPosition[0]), int(scaledTargetPosition[1]))
	else:
		scaledTargetPosition = None

	lastDisplayImage = cv2.resize(lastImage, (width, height), interpolation = cv2.INTER_AREA)

	if autoStretch:
		mono = lastDisplayImage.astype(np.float32)

		if autoStretchLower < autoStretchUpper:
			mono -= autoStretchLower
			print('AutoStretchLower:', autoStretchLower)
		else:
			mono -= autoStretchUpper
		stretchDelta = autoStretchUpper - autoStretchLower
		if stretchDelta < 0:
			stretchDelta = -stretchDelta
		elif stretchDelta == 0:
			stretchDelta = 1
		scaling = 65535.0 / stretchDelta
		mono *= scaling

		# Clamp 0-255
		mono = np.clip(mono, 0, 65535)
		mono = mono.astype(np.uint16)

		lastDisplayImage = mono

	if scaledTargetPosition is not None:
		print('Scaled Target Position:', scaledTargetPosition)
		drawTarget(lastDisplayImage, 10, 30, 1, scaledTargetPosition, [20000, 40000])

	window.panelFrame.widgetLastFrame.updateWithCVImage(lastDisplayImage)
	window.panelFrame.widgetControls.lastFrameLineEdit.setText('%d' % (ravf.frame_count()-1))
	window.panelFrame.widgetControls.timeLineEdit.setText(frameInfo['start_timestamp_date'] + ' ' + frameInfo['start_timestamp_time'])
	updateCurrentFrame()


def updateCurrentFrame():
	global window, current_frame

	window.panelFrame.widgetControls.currentFrameLineEdit.setText('%d' % current_frame)


def frameFirst():
	global ravf_fp, ravf, current_frame, targetPosition

	if ravf_fp is None or ravf is None:
		return

	targetPosition = None
	current_frame = 0
	getRavfFrame(current_frame)


def frameLast():
	global ravf_fp, ravf, current_frame, targetPosition

	if ravf_fp is None or ravf is None:
		return

	targetPosition = None
	current_frame = ravf.frame_count() - 1
	getRavfFrame(current_frame)


def framePrev():
	global ravf_fp, ravf, current_frame, targetPosition

	if ravf_fp is None or ravf is None:
		return

	targetPosition = None
	current_frame -= 1
	if current_frame < 0:
		current_frame = 0
	getRavfFrame(current_frame)


def frameNext():
	global ravf_fp, ravf, current_frame, targetPosition

	if ravf_fp is None or ravf is None:
		return

	targetPosition = None
	current_frame += 1
	if current_frame >= ravf.frame_count():
		current_frame = ravf.frame_count() - 1
	getRavfFrame(current_frame)


def playTimerCallback():
	if current_frame == (ravf.frame_count() - 1):
		togglePlay()
		return
	
	frameNext()


def togglePlay():
	global ravf_fp, ravf, playing, window, playTimer

	if ravf_fp is None or ravf is None:
		return

	if playing:
		playing = False
	else:
		playing = True

	window.panelFrame.widgetControls.buttonPlayPause.setText('Pause' if playing else 'Play')

	if playing:
		playTimer = QTimer()
		playTimer.timeout.connect(playTimerCallback)
		playTimer.setInterval(50)
		playTimer.start()
	else:
		playTimer.stop()



def setFrameNum(index):
	global ravf_fp, ravf, current_frame, window, targetPosition

	if ravf_fp is None or ravf is None:
		window.panelFrame.widgetControls.currentFrameLineEdit.setText('')
		return

	targetPosition = None
	current_frame = index
	if current_frame < 0:
		current_frame = 0
	if current_frame >= ravf.frame_count():
		current_frame = ravf.frame_count() - 1
	getRavfFrame(current_frame)


def setAutoStretchLimits(lower, upper):
	global current_frame, autoStretchLower, autoStretchUpper, autoStretch

	if lower < 0:
		lower = 0
	elif lower > 255:
		lower = 255

	if upper < 0:
		upper = 0
	elif upper > 255:
		upper = 255

	autoStretchUpper = upper * 256
	autoStretchLower = lower * 256

	getRavfFrame(current_frame)


def setAutoStretch(stretch):
	global autoStretch
	autoStretch = stretch
	getRavfFrame(current_frame)


def loadRavf(fname):
	global ravf_fp, ravf, current_frame, targetPosition, ravf_filename
	closeRavf()
		
	ravf_filename = fname
	print('loading ravf filename:', ravf_filename)

	ravf_fp = open(ravf_filename, 'rb')
	ravf = RavfReader(file_handle = ravf_fp)

	print('RAVF Version:', ravf.version())
	#print('Metadata:', ravf.metadata())
	#print('Timestamps:', ravf.timestamps())
	print('Frame Count:', ravf.frame_count())

	current_frame = 0
	targetPosition = None

	window.setWindowTitle('Player: %s' % os.path.basename(ravf_filename))
	getRavfFrame(current_frame)


def plateSolveStatusMsg(text):
	global window
	print(text)
	window.showStatusMessage(text)


def plateSolveSuccess(position, field_size, rotation_angle, index_file, focal_length, altAz):
	global ravf, targetPosition, current_frame, window

	print('Position:', position)
	print('Field Size:', field_size)
	print('Rotation Angle:', rotation_angle)
	print('Index File:', index_file)
	print('Focal Length:', focal_length)
	print('Alt Az:', altAz)

	f_basename = os.path.splitext(os.path.basename(plateSolveFitsFile))[0]
	f_dirname = os.path.dirname(plateSolveFitsFile)
	wcsFile = f_dirname + '/astrometry_tmp/' + f_basename + '.wcs'
	(ra, dec) = (ravf.metadata_value('RA'), ravf.metadata_value('DEC'))

	cmd = ['/usr/bin/wcs-rd2xy', '-w', wcsFile, '-r',  '%0.9f' % ra, '-d', '%0.9f' % dec]
	print(cmd)
	output = subprocess.check_output(cmd)
	print('Pixel conversion output:', output)
	output = str(output)
	output = output.split('-> pixel (')[1]
	output = output.split(')')[0]
	pixel_coord_target = output.split(', ')
	targetPosition = (float(pixel_coord_target[0]), float(pixel_coord_target[1]))

	print('Pixel Coordindates of the Target:', pixel_coord_target)	# Note these are coorindates in the original image, NOT the image on screen

	getRavfFrame(current_frame)

	window.panelOperations.plateSolveFinished()


def plateSolveCancel():
	global plateSolverThread
	if plateSolverThread is not None:
		print('Cancelling plate solver')
		plateSolverThread.cancel()
		window.showStatusMessage('**** Plate Solver Cancelled')
	window.panelOperations.plateSolveFinished()


def plateSolveFailed():
	print("Plate Solver Failed")
	window.showStatusMessage('**** Plate Solver Failed')
	window.panelOperations.plateSolveFinished()


def plateSolve():
	global ravf_fp, ravf, window, width, height, plateSolveFitsFile, plateSolverThread

	if ravf_fp is None or ravf is None:
		return

	frame = ravf.frame_by_index(ravf_fp, current_frame)

	if frame is None:
		raise ValueError('error reading frame: %d', current_frame)

	stride = ravf.metadata_value('IMAGE-ROW-STRIDE')
	ravf_height = ravf.metadata_value('IMAGE-HEIGHT')
	ravf_width = ravf.metadata_value('IMAGE-WIDTH')	

	if ravf.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_PACKED_10BIT.value:
		#print('Found 10bit packed')
		image = RavfImageUtils.bytes_to_np_array(frame.data, stride, ravf_height)
		image = RavfImageUtils.unstride_10bit(image, ravf_width, ravf_height)
		image = RavfImageUtils.unpack_10bit_pigsc(image, ravf_width, ravf_height, stride)

	search_full_sky = True

	fileHandling = FileHandling(Settings.getInstance().camera['photosFolder'], 'AstridPlayerSolve', FileHandlingImageType.PHOTO_LIGHT)

	metadata = {'ExposureTime': frame.exposure_duration/1000.0, 'AnalogueGain': ravf.metadata_value('INSTRUMENT-GAIN') }
	mode = {'size': (ravf_width, ravf_height), 'unpacked':'R10', 'bit_depth': 10}
	modeExtra = { 'bining': ravf.metadata_value('IMAGE-BINNING-X'), 'pixelSize':(3.45, 3.45), 'model': ravf.metadata_value('INSTRUMENT-SENSOR').txt }
	print('ModeExtra:', modeExtra)

	epoch = datetime(2010, 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo = timezone.utc) # 00:00:00 1st Jan 2010
	frame_seconds_since_epoch = timedelta(seconds = frame.start_timestamp / 1000000000)
	obsDateTime = epoch + frame_seconds_since_epoch

	focalLength = Settings.getInstance().platesolver['focal_length']
	position =  AstCoord.from360Deg(ravf.metadata_value('RA'), ravf.metadata_value('DEC'), 'icrs')

	imageData = image
	imageData = image.tobytes()
	imageData = np.frombuffer(imageData, dtype=np.uint8)
	imageData = imageData.reshape(ravf_height, ravf_width * 2)

	plateSolveFitsFile = fileHandling.save_photo_fit(imageData, metadata, mode, modeExtra, obsDateTime, focalLength, position)

	print('Plate Solving')
	plateSolverThread = PlateSolver(plateSolveFitsFile, search_full_sky, progress_callback=plateSolveStatusMsg, success_callback=plateSolveSuccess, failure_callback=plateSolveFailed)


def savePng():
	global ravf_fp, ravf, lastDisplayImage, ravf_filename, current_frame, window

	if ravf_fp is None or ravf is None:
		return

	f_basename = os.path.splitext(ravf_filename)[0]

	img_filename = '%s_frame_%d.png' % (f_basename, current_frame)
		
	print('Saving frame (and solve) to:', img_filename)
	cv2.imwrite(img_filename, lastDisplayImage)

	window.showStatusMessage('Saved frame to: %s' % img_filename)


def saveFits():
	global ravf_fp, ravf, lastImage, ravf_filename, current_frame, window, frameStatus, targetPosition

	if ravf_fp is None or ravf is None:
		return

	f_basename = os.path.splitext(ravf_filename)[0]

	img_filename = '%s_frame_finder_%d.fit' % (f_basename, current_frame)

	print('Saving frame to:', img_filename)

	start_timestamp = frameStatus['start_timestamp']
	epoch = datetime(2010, 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo = timezone.utc) # 00:00:00 1st Jan 2010
	frame_seconds_since_epoch = timedelta(seconds = start_timestamp / 1000000000)
	obsDateTime = epoch + frame_seconds_since_epoch
	#print(obsDateTime)
	expTime = frameStatus['exposure_duration'] / 1000000000.0

	if targetPosition is not None:
		print('Target Position:', targetPosition)
		drawTarget(lastImage, 20, 60, 1, (int(targetPosition[0]), int(targetPosition[1])), [0, 65535])
	
	save_fits_frame(lastImage, img_filename, obsDateTime, expTime, current_frame)

	window.showStatusMessage('Saved frame to: %s' % img_filename)


def __decimalDegreesToDMS(deg):
	# Converts decimal degrees to dms for lat/lon
	d = int(deg)
	mins = (deg - d) * 60.0
	m = int(mins)
	s = (mins - m) * 60.0

	m = abs(m)
	s = abs(s)

	return (d, m, s)

	
def save_fits_frame(arr, fname, obsDateTime, expTime, sequence):
	global ravf

	hdu = fits.PrimaryHDU(arr)
	hdul = fits.HDUList([hdu])

	hdr = hdul[0].header

	hdr['INSTRUME']	= '%s:%s' % (ravf.metadata_value('INSTRUMENT'), ravf.metadata_value('INSTRUMENT-SENSOR'))
	hdr['OBJECT']	= str(ravf.metadata_value('OBJNAME'))
	hdr['TELESCOP']	= str(ravf.metadata_value('TELESCOPE'))

	hdr['EXPTIME']	= expTime
	hdr['OBS_ID']	= '%06d' % sequence

	if ravf.metadata_value('SENSOR-PIXEL-SIZE-X') is not None:
		hdr['XPIXSZ']	= ravf.metadata_value('INSTRUMENT-SENSOR-PIXEL-SIZE-X')
	if ravf.metadata_value('SENSOR-PIXEL-SIZE-Y') is not None:
		hdr['YPIXSZ']	= ravf.metadata_value('INSTRUMENT-SENSOR-PIXEL-SIZE-Y')

	hdr['XBINNING']	= ravf.metadata_value('IMAGE-BINNING-X')
	hdr['YBINNING']	= ravf.metadata_value('IMAGE-BINNING-Y')

	if ravf.metadata_value('FOCAL-LENGTH') is not None:
		hdr['FOCALLEN']	= ravf.metadata_value('FOCAL-LENGTH')

	hdr['IMAGETYP']	= 'Light Frame'
	hdr['GAIN']	= ravf.metadata_value('INSTRUMENT-GAIN')
	hdr['OFFSET']	= ravf.metadata_value('INSTRUMENT-OFFSET')
	hdr['CVF']	= 0.0
	hdr['PROGRAM']	= str(ravf.metadata_value('RECORDER-SOFTWARE'))

	(d, m, s) = __decimalDegreesToDMS(ravf.metadata_value('LATITUDE'))
	hdr['SITELAT']	= '%3d %02d %0.3f' % (d, m, s)
	(d, m, s) = __decimalDegreesToDMS(ravf.metadata_value('LONGITUDE'))
	hdr['SITELONG']	= '%3d %02d %0.3f' % (d, m, s)

	hdr['RA']	= ravf.metadata_value('RA')
	hdr['DEC']	= ravf.metadata_value('DEC')

	if ravf.metadata_value('COLOR-TYPE') != 0:
		if ravf.metadata_value('COLOR_TYPE') == 4:
			hdr['BAYERPAT']	= 'BGGR'
		hdr['XBAYROFF'] = 0
		hdr['YBAYROFF'] = 0

	hdr['BSCALE']	= 1.0
	hdr['BZERO']	= 32768.0
	file_creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
	obs_time = obsDateTime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
	hdr['DATE']	= file_creation_time		# Time of file creation UTC
	hdr['DATE-OBS']	= obs_time			# Start Time of the observation UTC
	hdr['ROWORDER'] = 'TOP-DOWN'			# Siril Request - Reference: https://free-astro.org/index.php?title=Siril:FITS_orientation

	#print(repr(hdu.header))

	hdul.writeto(fname, overwrite=True)
	hdul.close()


def exportFits():
	global ravf_fp, ravf, playing, ravf_filename, current_frame, window, lastImage, frameInfo, frameStatus, thread, exportFitsSeqMsgBox

	if ravf_fp is None or ravf is None:
		return

	if playing:
		togglePlay()

	if QMessageBox.information(window, ' ', 'Astrid writes the RAVF video file format which can be read in PyMovie for light curve analysis.  RAVF contains a detailed audit trail, metadata and is raw data.\n\nFITS Sequence Export is provided here as a convenience for software that does not yet support the RAVF file format, however in the conversion process the audit trail and some of the metadata will be sacrificed.\n\nRAVF is always the preferred choice of file format for Astrid video files as zipping up 1000\'s of individual fits files for video is an inefficient and cumbersome form of storage/transfer.\n\nPlease contact the developer of your application and ask that they support the RAVF format.', QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Cancel:
		return

	thread = ExportFitsSequenceThread()
	thread.exportFitsSequenceFinished.connect(__exportFitsSequenceFinished)
	thread.exportFitsSequenceStatus.connect(__exportFitsSequenceStatus)
	#thread.finished.connect(self.thread.deleteLater)
	thread.start()

	exportFitsSeqMsgBox = QMessageBox()
	exportFitsSeqMsgBox.setIcon(QMessageBox.Information)
	exportFitsSeqMsgBox.setText('Please wait, exporting fits sequence...')
	exportFitsSeqMsgBox.setStandardButtons(QMessageBox.Cancel)

	if exportFitsSeqMsgBox.exec() == QMessageBox.Cancel:
		thread.terminate_now = True


def __exportFitsSequenceStatus(text):
	global window
	window.showStatusMessage(text)


def __exportFitsSequenceFinished():
	global thread, exportFitsSeqMsgBox
	thread.wait()
	thread = None
	exportFitsSeqMsgBox.done(0)
	exportFitsSeqMsgBox = None
	frameFirst()


def metadata():
	txt = ''
	for entry in ravf.metadata():
		txt += '%s: %s\n' % (entry[0], str(entry[1]))
	return txt[:-1]




if __name__ == '__main__':

	stylesheets_folder	= '../app/stylesheets'
	stylesheet		= '%s/default.qss' % stylesheets_folder

	ravf_fp			= None
	ravf			= None
	playing			= False
	playTimer		= None
	autoStretch		= False
	autoStretchLower	= 0
	autoStretchUpper	= 65535
	plateSolveFitsFile	= None
	plateSolverThread	= None
	targetPosition		= None
	lastDisplayImage	= None
	lastImage		= None
	ravf_filename		= None
	frameInfo		= None
	frameStatus		= None
	thread			= None
	exportFitsSeqMsgBox	= None

	width		= int(1456/2)
	height		= int(1088/2)

	current_frame	= 0


	def checkAstridDrivePresent() -> bool:
		if not os.path.isdir(astrid_drive):
			dialog = UiDialogPanel('ASTRID USB thumb drive not found', UiPanelMessage, args = {'msg': 'Troubleshooting:\n    1. Insert USB Drive in blue USB port on ASTRID and try again', 'buttonText': 'Quit'})
			return False
		return True


	def setStylesheet():
		""" Reads a stylesheet and using colorscheme, replaces the color macros """	
		ss = AstUtils.read_file_as_string(stylesheet)

		if os.path.exists(configs_fname):
			with open(configs_fname, 'r') as fp:
				configs = json.load(fp)

			if 'selectedColorScheme' not in configs.keys():
				configs['selectedColorScheme'] = 'Astro'
	
				jstr = json.dumps(configs, indent=4)
	
				with open(configs_fname, 'w') as fp:
					fp.write(jstr)
	
				colorSchemeName = configs['selectedColorScheme']
			else:
				colorSchemeName = configs['selectedColorScheme']
		else:
			colorSchemeName = 'Astro'
	
		with open('%s/%s.colorscheme' % (stylesheets_folder, colorSchemeName)) as f:
			cs = json.loads(f.read())
	
		# Do Macro search and replace
		for key in cs.keys():
			ss = ss.replace(key, cs[key])

		app.setStyleSheet(ss)	# Set the stylesheet


	#
	# MAIN
	#

	# Parse arguments
	parser = argparse.ArgumentParser(description="astrid", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-d', '--astrid_drive', help ='path to astrid drive', required=True)
	args = parser.parse_args()
	astrid_drive = args.astrid_drive
	configs_fname = astrid_drive + '/configs/configs.json'

	print('command args: %s' % sys.argv)
	print('astrid_drive: %s' % astrid_drive)

	with open(configs_fname, 'r') as fp:
		configs = json.load(fp)
	selectedIndex = configs['selectedIndex']
	configBase = os.path.dirname(configs_fname)
	settings_folder = configBase + '/' + configs['configs'][selectedIndex]['configFolder']
	Settings(settings_folder, astrid_drive, astrid_drive + '/configs')

	# Start the QtApplication
	app = QApplication([])

	# Read Stylesheet
	setStylesheet()

	# Check the ASTRID drive is present
	if not checkAstridDrivePresent():
		print('Error: ASTRID flash drive not present, aborting...')
		sys.exit(0)

	# Start the main window
	window = UiPlayer('Player', astrid_drive, loadRavf, width, height, frameFirst, frameLast, framePrev, frameNext, togglePlay, setFrameNum)
	window.panelOperations.setCallbacks(setAutoStretch, setAutoStretchLimits, plateSolve, plateSolveCancel, savePng, saveFits, exportFits, metadata)

	QMessageBox.warning(window, ' ', 'Astrid Player currently obtains the focal length and various settings from the currently chosen configuration in Astrid.\n\nPlease ensure the matching configuration that the video was taken with is selected in Astrid.\n\nIf plate solving fails, then this is the likely cause.', QMessageBox.Ok)

	exit_code = app.exec()
	closeRavf()
	sys.exit(exit_code)
