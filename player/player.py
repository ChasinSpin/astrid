#!/usr/bin/env python3

import os
import sys
import json
import argparse

sys.path.append('../app')

import cv2
from UiPlayer import UiPlayer
from astutils import AstUtils
from UiDialogPanel import UiDialogPanel
from UiPanelMessage import UiPanelMessage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from ravf import RavfReader, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox, RavfImageUtils





def closeRavf():
	global ravf_fp, ravf
	if ravf_fp is not None:
		ravf_fp.close() 
		ravf = None
		ravf_fp = None


def getRavfFrame(index):
	global ravf_fp, ravf, window, width, height

	(err, image, frameInfo, status) = ravf.getPymovieMainImageAndStatusData(ravf_fp, index)

	if err:
		raise ValueError('error reading frame: %d', index)

	print(image.shape)
	image = cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)
	window.panelFrame.widgetLastFrame.updateWithCVImage(image)
	window.panelFrame.widgetControls.lastFrameLineEdit.setText('%d' % (ravf.frame_count()-1))
	updateCurrentFrame()


def updateCurrentFrame():
	global window, current_frame

	window.panelFrame.widgetControls.currentFrameLineEdit.setText('%d' % current_frame)


def frameFirst():
	global ravf_fp, ravf, current_frame

	current_frame = 0
	getRavfFrame(current_frame)


def frameLast():
	global ravf_fp, ravf, current_frame

	current_frame = ravf.frame_count() - 1
	getRavfFrame(current_frame)


def framePrev():
	global ravf_fp, ravf, current_frame

	current_frame -= 1
	if current_frame < 0:
		current_frame = 0
	getRavfFrame(current_frame)


def frameNext():
	global ravf_fp, ravf, current_frame

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

	if playing:
		playing = False
	else:
		playing = True

	window.panelFrame.widgetControls.buttonPlayPause.setText('Pause' if playing else 'Play')

	if playing:
		playTimer = QTimer()
		playTimer.timeout.connect(playTimerCallback)
		playTimer.setInterval(100)
		playTimer.start()
	else:
		playTimer.stop()



def setFrameNum(index):
	global ravf_fp, ravf, current_frame

	current_frame = index
	if current_frame < 0:
		current_frame = 0
	if current_frame >= ravf.frame_count():
		current_frame = ravf.frame_count() - 1
	getRavfFrame(current_frame)


def loadRavf(fname):
	global ravf_fp, ravf, current_frame
	closeRavf()
		
	print('loading ravf filename:', fname)

	ravf_fp = open(fname, 'rb')
	ravf = RavfReader(file_handle = ravf_fp)

	print('RAVF Version:', ravf.version())
	#print('Metadata:', ravf.metadata())
	#print('Timestamps:', ravf.timestamps())
	print('Frame Count:', ravf.frame_count())

	current_frame = 0
	getRavfFrame(current_frame)





if __name__ == '__main__':

	stylesheets_folder	= '../app/stylesheets'
	stylesheet		= '%s/default.qss' % stylesheets_folder

	ravf_fp		= None
	ravf		= None
	playing		= False
	playTimer	 = None

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

	exit_code = app.exec()
	closeRavf()
	sys.exit(exit_code)
