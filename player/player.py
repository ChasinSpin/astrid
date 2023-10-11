#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess

sys.path.append('../app')

import cv2
import numpy as np
from UiPlayer import UiPlayer
from astutils import AstUtils
from UiDialogPanel import UiDialogPanel
from UiPanelMessage import UiPanelMessage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from ravf import RavfReader, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox, RavfImageUtils
from FileHandling import *
from astcoord import AstCoord
from datetime import timedelta, timezone
from PlateSolver import PlateSolver
from settings import Settings



def closeRavf():
	global ravf_fp, ravf
	if ravf_fp is not None:
		ravf_fp.close() 
		ravf = None
		ravf_fp = None


def getRavfFrame(index):
	global ravf_fp, ravf, window, width, height, autoStretch, autoStretchLower, autoStretchUpper, targetPosition, lastImage

	if ravf_fp is None or ravf is None:
		return

	(err, image, frameInfo, status) = ravf.getPymovieMainImageAndStatusData(ravf_fp, index)

	if err:
		raise ValueError('error reading frame: %d', index)

	#print(image.shape)

	if targetPosition is not None:
		scaledTargetPosition = (targetPosition[0] * (width/image.shape[1]), targetPosition[1] * (height/image.shape[0]))
		scaledTargetPosition = (int(scaledTargetPosition[0]), int(scaledTargetPosition[1]))
	else:
		scaledTargetPosition = None

	image = cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

	if autoStretch:
		mono = image.astype(np.float32)

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

		image = mono

	if scaledTargetPosition is not None:
		print('Scaled Target Position:', scaledTargetPosition)

		lineGap = 10
		lineLength = 30
		x = scaledTargetPosition[0]
		y = scaledTargetPosition[1]
		cv2.line(image, (x, y-lineGap), (x, y-lineLength), (32000), 3)
		cv2.line(image, (x, y+lineGap), (x, y+lineLength), (32000), 3)
		cv2.line(image, (x-lineGap, y), (x-lineLength, y), (32000), 3)
		cv2.line(image, (x+lineGap, y), (x+lineLength, y), (32000), 3)

	lastImage = image

	window.panelFrame.widgetLastFrame.updateWithCVImage(image)
	window.panelFrame.widgetControls.lastFrameLineEdit.setText('%d' % (ravf.frame_count()-1))
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
	global playing, window, playTimer

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


def saveFrame():
	global lastImage, ravf_filename, current_frame, window

	if ravf_fp is None or ravf is None:
		return

	f_basename = os.path.splitext(ravf_filename)[0]

	img_filename = '%s_frame_%d.png' % (f_basename, current_frame)
		
	print('Saving frame (and solve) to:', img_filename)
	cv2.imwrite(img_filename, lastImage)

	window.showStatusMessage('Saved frame to: %s' % img_filename)


	
	



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
	lastImage		= None
	ravf_filename		= None

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
	window.panelOperations.setCallbacks(setAutoStretch, setAutoStretchLimits, plateSolve, plateSolveCancel, saveFrame)

	QMessageBox.warning(window, ' ', 'Astrid Player currently obtains the focal length and various settings from the currently chosen configuration in Astrid.\n\nPlease ensure the matching configuration that the video was taken with is selected in Astrid.\n\nIf plate solving fails, then this is the likely cause.', QMessageBox.Ok)

	exit_code = app.exec()
	closeRavf()
	sys.exit(exit_code)
