#!/usr/bin/env python3

import os
import sys
import json
import atexit
import argparse
import logging
from Ui import Ui
from settings import Settings
from astsite import AstUtils
from UiDialogPanel import UiDialogPanel
from UiPanelConfig import UiPanelConfig
from UiPanelMessage import UiPanelMessage
from UiSplashScreen import UiSplashScreen
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPixmap
from CameraModel import CameraModel, OperatingMode
from processlogger import ProcessLogger
from otestamper import OteStamper
from framewriter import FrameWriter
import time
import multiprocessing

if __name__ == '__main__':

	stylesheet	= 'stylesheets/default.qss'
	settings_folder	= None
	settings_summar	= None
	cam		= None
	otestamper	= None
	framewriter	= None
	processes	= []



	def shutdown_subprocesses():
		global cam, processes, otestamper

		if processes is not None:
			print('TERMINATE: shutting down multiprocessing subprocesses, pid: %d' % os.getpid())
			for process in processes:
				process.terminate()
			processes = None
	
		if cam is not None:
			print('TERMINATE: shutting down camera, pid: %d' % os.getpid())
			print('TERMINATE: shutting down indi server, pid: %d' % os.getpid())
			cam.indi.killIndiServer()
			cam = None
	


	# Things to do when sys.exit is called
	@atexit.register
	def sysexit_handler():
		print('TERMINATE: sysexit_handler, pid: %d **PLEASE WAIT**' % os.getpid())
		shutdown_subprocesses()


	def handle_exception(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			sys.__excepthook__(exc_type, exc_value, exc_traceback)
			logger.critical('Keyboard interrupt')
			shutdown_subprocesses()
			sys.exit(-3)
		else:
			logger.critical("uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
			#sys.__excepthook__(exc_type, exc_value, exc_traceback)
			shutdown_subprocesses()
			sys.exit(-2)


	def settingsCallback(folder, summary):
		global settings_folder, settings_summary

		if folder is None or summary is None:
			splash_screen.close()
			logger.warning('user changed config, aborting so that the user can relaunch with the new config...')
			shutdown_subprocesses()
			sys.exit(0)
		else:
			settings_folder = folder
			settings_summary = summary


	def getConfig(configs_fname):
		dialog = UiDialogPanel('Choose Config', UiPanelConfig, args = {'configs_fname': configs_fname, 'astrid_drive': astrid_drive, 'settings_callback': settingsCallback, 'stylesheet_callback': setStylesheet})


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
	
		with open('stylesheets/%s.colorscheme' % colorSchemeName) as f:
			cs = json.loads(f.read())
	
		# Do Macro search and replace
		for key in cs.keys():
			ss = ss.replace(key, cs[key])

		app.setStyleSheet(ss)	# Set the stylesheet


	#
	# MAIN
	#

	sys.excepthook = handle_exception

	# Parse arguments
	parser = argparse.ArgumentParser(description="astrid", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-d', '--astrid_drive', help ='path to astrid drive', required=True)
	args = parser.parse_args()
	astrid_drive = args.astrid_drive
	configs_fname = astrid_drive + '/configs/configs.json'
	log_filename = astrid_drive + '/astrid.log'

	# Setup logger
	multiprocessing.set_start_method('forkserver')
	#multiprocessing.set_start_method('spawn')

	if os.path.isdir(astrid_drive):
		processLogger = ProcessLogger(log_filename = log_filename, logging_level=logging.DEBUG)
		processes.append(processLogger)
		logger = processLogger.getLogger()
	else:
		logger = logging.getLogger()

	logger.debug('command args: %s' % sys.argv)
	logger.debug('astrid_drive: %s' % astrid_drive)


	# Start the QtApplication
	app = QApplication([])

	splash_screen = UiSplashScreen()

	# Read Stylesheet
	splash_screen.setMessage('Loading: Reading stylesheet...')
	setStylesheet()

	# Check the ASTRID drive is present
	if not checkAstridDrivePresent():
		logger.error('ASTRID flash drive not present, aborting...')
		shutdown_subprocesses()
		sys.exit(0)

	# Launch OTEStamper
	otestamper = OteStamper()
	processes.append(otestamper)

	# Launch FrameWriter
	framewriter = FrameWriter()
	processes.append(framewriter)

	# Read settings
	splash_screen.setMessage('Loading: Reading settings...')
	getConfig(configs_fname)
	if settings_folder is None:
		splash_screen.close()
		logger.warning('user cancelled config, aborting...')
		shutdown_subprocesses()
		sys.exit(0)

	# Load the camera
	try:
		cam = CameraModel(previewWidth=640, previewHeight=480, splashScreen=splash_screen)
	except RuntimeError:
		# This never gets called as exitNow is called after this object has been created
		shutdown_subprocesses()
		sys.exit(0)

	# Start the main window
	windowTitle = 'Astrid: %s' % settings_summary
	window = Ui(cam, windowTitle)

	# Finish setup and close the splash screen
	cam.ui = window
	otestamper.setUi(window)
	splash_screen.close()
	cam.updateMountPositionDisplay()

	# Display the status
	window.showStatusMessage("Astrid started")

	exit_code = app.exec()
	shutdown_subprocesses()
	sys.exit(exit_code)
