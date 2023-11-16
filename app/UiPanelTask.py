import os
import time
import math
from UiPanel import UiPanel
from CameraModel import OperatingMode
from settings import Settings
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from astcoord import AstCoord
from UiQDialog import UiQDialog
from starcatalog import StarLookup, Star
from UiDialogPanel import UiDialogPanel
from UiPanelExposureChart import UiPanelExposureChart


class UiPanelTask(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Task')
		self.camera		= camera
		options = ['Photo', 'OTE Video']
		self.settings_mount = Settings.getInstance().mount
		if self.settings_mount['align_axis'] == 'eq' and self.settings_mount['goto_capable'] and self.settings_mount['tracking_capable']:
			options.append('Polar Align')
		self.widgetTask		= self.addComboBox('Task', options)
		self.widgetTask.setObjectName('comboBoxTask')
		self.widgetFrameRate	= self.addLineEditDouble('Frame Rate(fps)', 0.0, 600.38, 2)
		self.widgetFrameRate.setText('10.0')
		self.widgetExposure	= self.addLineEditDouble('Exposure(s)', 0.000000, 15.534385, 6)
		self.widgetExposure.setText(str(Settings.getInstance().camera['default_photo_exposure']))
		self.widgetGain		= self.addLineEditDouble('Gain', 1.000000, 16.0, 1)
		self.widgetGain.setText(str(Settings.getInstance().camera['gain']))
		self.widgetNumSubs	= self.addLineEditInt('# Subs', 1, 10000)
		self.widgetNumSubs.setText('1')
		self.widgetJobName	= self.addLineEdit('Job Name')
		self.widgetJobName.setText('None')
		if self.settings_mount['goto_capable']:
			self.widgetDither	= self.addCheckBox('Dither')
		self.widgetFullSkySolve	= self.addCheckBox('Full Sky Solve')
		self.widgetFullSkySolve.setChecked(True)
		self.camera.setFullSkySolve(True)
		self.widgetPlateSolve	= self.addButton('Plate Solve')
		self.spacer		= self.addSpacer()
		self.widgetRecord	= self.addButton('', fullWidth=False, checkable=True)
		self.widgetRecord.setObjectName('taskRecord')
		self.widgetPANext	= self.addButton('Next')
		self.plateSolveDialog	= None


	def update_ui_for_mode(self, opMode):
		if   opMode == OperatingMode.PHOTO:
			self.hideWidget(self.widgetFrameRate)
			self.showWidget(self.widgetExposure)
			self.showWidget(self.widgetGain)
			self.showWidget(self.widgetNumSubs)
			self.showWidget(self.widgetJobName)
			if self.settings_mount['goto_capable']:
				self.showWidget(self.widgetDither)
			self.showWidget(self.widgetFullSkySolve)
			self.showWidget(self.widgetRecord)
			self.showWidget(self.widgetPlateSolve)
			self.hideWidget(self.widgetPANext)
		elif opMode == OperatingMode.POLAR_ALIGN:
			self.hideWidget(self.widgetFrameRate)
			self.showWidget(self.widgetExposure)
			self.showWidget(self.widgetGain)
			self.hideWidget(self.widgetNumSubs)
			self.hideWidget(self.widgetJobName)
			if self.settings_mount['goto_capable']:
				self.hideWidget(self.widgetDither)
			self.showWidget(self.widgetFullSkySolve)
			self.hideWidget(self.widgetRecord)
			self.hideWidget(self.widgetPlateSolve)
			self.showWidget(self.widgetPANext)
		elif opMode == OperatingMode.OTE_VIDEO:
			self.showWidget(self.widgetFrameRate)
			self.hideWidget(self.widgetExposure)
			self.showWidget(self.widgetGain)
			self.hideWidget(self.widgetNumSubs)
			self.showWidget(self.widgetJobName)
			if self.settings_mount['goto_capable']:
				self.hideWidget(self.widgetDither)
			self.hideWidget(self.widgetFullSkySolve)
			self.showWidget(self.widgetRecord)
			self.hideWidget(self.widgetPlateSolve)
			self.hideWidget(self.widgetPANext)
		else:
			raise ValueError('OperatingMode not valid')



	def registerCallbacks(self):
		self.widgetTask.currentTextChanged.connect(self.comboBoxTaskChanged)
		self.widgetFrameRate.editingFinished.connect(self.lineEditFrameRateChanged)
		self.widgetExposure.editingFinished.connect(self.lineEditExposureChanged)
		self.widgetGain.editingFinished.connect(self.lineEditGainChanged)
		self.widgetNumSubs.editingFinished.connect(self.lineEditNumSubsChanged)
		self.widgetJobName.editingFinished.connect(self.lineEditJobNameChanged)
		if self.settings_mount['goto_capable']:
			self.widgetDither.stateChanged.connect(self.checkBoxDitherChanged)
		self.widgetFullSkySolve.stateChanged.connect(self.checkBoxFullSkySolveChanged)
		self.widgetRecord.clicked.connect(self.buttonRecordPressed)
		self.widgetPlateSolve.clicked.connect(self.buttonPlateSolvePressed)
		self.widgetPANext.clicked.connect(self.buttonPANextPressed)



	# CALLBACKS

	def comboBoxTaskChanged(self, text):
		if text == 'Photo':
			self.camera.switchMode(OperatingMode.PHOTO)
		elif text == 'Polar Align':
			self.camera.switchMode(OperatingMode.POLAR_ALIGN)
		elif text == 'OTE Video':
			self.camera.switchMode(OperatingMode.OTE_VIDEO)
		elif text == 'Video':
			self.camera.switchMode(OperatingMode.VIDEO)
		else:
			raise ValueError('OperatingMode not valid')
		self.update_ui_for_mode(self.camera.operatingMode)


	def lineEditFrameRateChanged(self):
		txt = self.widgetFrameRate.text()
		print('Line Edit Frame Rate Changed:', txt)
		fps = float(txt)
		self.camera.configureVideoFrameRate(fps)


	def lineEditExposureChanged(self):
		txt = self.widgetExposure.text()
		print('Line Edit Exposure Changed:', txt)
		exp = float(txt)
		self.camera.configureStillExposureTime(exp)


	def lineEditGainChanged(self):
		txt = self.widgetGain.text()
		print('Line Edit Gain Changed:', txt)
		gain = float(txt)
		self.camera.setGain(gain)


	def lineEditNumSubsChanged(self):
		txt = self.widgetNumSubs.text()
		count = int(txt)
		self.camera.setPhotoCountTotal(count)


	def __sanitizeJobName(self, txt):
		txt = txt.replace(' ', '_')
		txt = txt.replace('.', '_')
		return txt
	

	def lineEditJobNameChanged(self):
		txt = self.widgetJobName.text()
		txt2 = self.__sanitizeJobName(txt)
		if txt2 != txt:
			txt = txt2
			self.widgetJobName.setText(txt)
		self.camera.setJobName(txt)


	def checkBoxDitherChanged(self):
		state = self.widgetDither.checkState()
		tState = False
		if state == 2:
			tState = True
		self.camera.setDither(tState)


	def checkBoxFullSkySolveChanged(self):
		state = self.widgetFullSkySolve.checkState()
		tState = False
		if state == 2:
			tState = True
		self.camera.setFullSkySolve(tState)


	def buttonRecordPressed(self, checked):
		print('Button Record Pressed:', checked)

	def buttonRecordPressed(self, checked):
		print('Button Record Pressed:', checked)
		if checked:
			self.camera.startRecording()
		else:
			self.camera.stopRecording()


	def buttonPlateSolvePressed(self, checked, expAnalysis = False):
		if self.camera.lastFitFile == 'dummy.fit':
			QMessageBox.warning(self, ' ', 'No photo to plate solve, take a photo first!', QMessageBox.Ok)
		else:
			if self.camera.filePlateSolve:
				fname = QFileDialog.getOpenFileName(self, 'Open file', Settings.getInstance().astrid_drive, 'FITS files (*.fit)')[0]
				if len(fname) != 0:
					print('Filename:', fname)
					self.camera.lastFitFile = fname
					self.camera.updateDisplayOptions()
				else:
					return

			self.camera.solveField(self.camera.lastFitFile, expAnalysis)
			self.launchPlateSolveWidget(expAnalysis)


	def launchPlateSolveWidget(self, expAnalysis):
		self.plateSolveDialog = UiQDialog(parent = self.camera.ui, topLeft = (260, 20))
		self.plateSolveDialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)

		self.plateSolveDialog.plateSolvePanel = UiPanel('Plate Solver')	
		panel = self.plateSolveDialog.plateSolvePanel
		panel.msg	= panel.addLabel('Plate Solving...')
		panel.ra	= panel.addLineEdit('RA', editable=False)
		panel.hideWidget(panel.ra)
		panel.dec	= panel.addLineEdit('DEC', editable=False)
		panel.hideWidget(panel.dec)
		panel.focalLen	= panel.addLineEdit('Focal Length', editable=False)
		panel.hideWidget(panel.focalLen)
		panel.fov	= panel.addLineEdit('FOV', editable=False)
		panel.hideWidget(panel.fov)
		panel.rotation	= panel.addLineEdit('Rotation', editable=False)
		panel.hideWidget(panel.rotation)
		panel.index	=panel.addLineEdit('Index', editable=False)
		panel.hideWidget(panel.index)
		if self.settings_mount['goto_capable']:
			panel.syncGoto	= panel.addButton('Sync and Goto')
			panel.hideWidget(panel.syncGoto)
		else:
			direction_indicator_platesolve = Settings.getInstance().platesolver['direction_indicator_platesolve']
			if direction_indicator_platesolve != 'None':
				panel.altAzDirection = panel.addAltAzDirection()
				panel.hideWidget(panel.altAzDirection)
			else:
				panel.altAzDirection = None
		panel.syncOnly	= panel.addButton('Sync Only')
		panel.hideWidget(panel.syncOnly)
		panel.ok	= panel.addButton('OK')
		panel.hideWidget(panel.ok)


		if expAnalysis:
			panel.displayChart	= panel.addButton('Display Analysis Chart')
			panel.overlayMagnitudes	= panel.addButton('Overlay Magnitudes ')
			panel.displayChart.clicked.connect(self.buttonDisplayChartPressed)
			panel.overlayMagnitudes.clicked.connect(self.buttonOverlayMagnitudesPressed)
			panel.hideWidget(panel.displayChart)
			panel.hideWidget(panel.overlayMagnitudes)
		else:
			panel.displayChart	= None
			panel.overlayMagnitudes	= None
		panel.cancel	= panel.addButton('Cancel')

		# Setup Callbacks
		panel.syncOnly.clicked.connect(self.buttonPlateSolveSyncOnlyPressed)
		if self.settings_mount['goto_capable']:
			panel.syncGoto.clicked.connect(self.buttonPlateSolveSyncGotoPressed)
		panel.ok.clicked.connect(self.buttonPlateSolveOkPressed)
		panel.cancel.clicked.connect(self.buttonPlateSolveCancelPressed)

		self.plateSolveDialogLayout = QVBoxLayout()
		self.plateSolveDialogLayout.addWidget(panel)
		self.plateSolveDialog.setLayout(self.plateSolveDialogLayout)

		self.plateSolveDialog.exec()


	def updatePlateSolveSuccess(self, coord, field_size, rotation_angle, index_file, focal_length, altAzPlateSolve, expAnalysis = False):
		if self.plateSolveDialog is not None:
			ra = ''
			dec = ''
			if coord is not None:
				(ra, dec) = coord.raDecStrForSettingFormat('icrs')

			panel = self.plateSolveDialog.plateSolvePanel

			panel.ra.setText(ra)
			panel.dec.setText(dec)
			panel.focalLen.setText(str(int(focal_length)) + 'mm')
			panel.fov.setText(field_size)
			panel.rotation.setText(rotation_angle)
			panel.index.setText(index_file)
			panel.showWidget(self.plateSolveDialog.plateSolvePanel.cancel)
			panel.msg.setText('Plate Solve SUCCESS!')
			panel.showWidget(panel.ra)
			panel.showWidget(panel.dec)
			panel.showWidget(panel.focalLen)
			panel.showWidget(panel.fov)
			panel.showWidget(panel.rotation)
			panel.showWidget(panel.index)
			if self.settings_mount['goto_capable']:
				if not expAnalysis:
					panel.showWidget(panel.syncGoto)
			else:
				if self.camera.objectCoords is not None and panel.altAzDirection is not None:
					direction_indicator_platesolve = Settings.getInstance().platesolver['direction_indicator_platesolve']
					altAzDelta = self.calculateAltAzDelta(altAzPlateSolve, self.camera.objectCoords)
					panel.showWidget(panel.altAzDirection)
					panel.altAzDirection.update(altAzDelta[0], altAzDelta[1], direction_indicator_platesolve)

			if expAnalysis:
				panel.showWidget(panel.displayChart)
				panel.showWidget(panel.overlayMagnitudes)
			else:
				panel.showWidget(panel.syncOnly)
			panel.adjustSize()
			self.plateSolveDialog.adjustSize()
			self.plateSolveDialog.show()
			self.plateSolveDialog.centerInParent()


	def calculateAltAzDelta(self, altAzPlateSolve, targetCoords):
		altAzTarget = self.camera.objectCoords.altAzRefracted(frame='icrs')

		print('AltAzTarget:', altAzTarget)
		print('AltAzPlateSolve:', altAzPlateSolve)

		# Calculate delta
		# 	Az: negative is rotate anti clockclockwise, positive is rotate clockwise
		# 	Alt: negative is move down, positive is move up
		deltaAlt = altAzTarget[0] - altAzPlateSolve[0]
		deltaAz = altAzTarget[1] - altAzPlateSolve[1]
	
		# Calculate nearest azimuth direction if it's more than 180 degrees to the target
		if deltaAz > 180.0:
			deltaAz = -(360.0 - deltaAz)
		elif deltaAz < -180.0:
			deltaAz = -(-360.0 - deltaAz)

		return (deltaAlt, deltaAz)


	def updatePlateSolveFailed(self):
		if self.plateSolveDialog is not None:
			self.plateSolveDialog.plateSolvePanel.msg.setText('Plate Solve FAILED!\n\nFailure can be due to the following reasons:\n   1. Poor focus (excellent focus is required)\n   2. Wrong astrometry index files for focal length\n   3. Scope pointing outside of search radius from expected RA/DEC (try Full Sky Solve)\n   4. Incorrect focal length\n   5. Partial or complete cloud cover\n   6. Exposure too short\n   7. Drift due to polar alignment and length of exposure')
			self.plateSolveDialog.plateSolvePanel.hideWidget(self.plateSolveDialog.plateSolvePanel.cancel)
			self.plateSolveDialog.plateSolvePanel.showWidget(self.plateSolveDialog.plateSolvePanel.ok)


	def launchPolarAlignDirectionDialog(self, altAzDelta):
		alt = altAzDelta[0]
		az = altAzDelta[1]

		self.directionDialog = UiQDialog(parent = self.camera.ui, topLeft = (260, 20))
		self.directionDialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)

		self.directionDialog.directionPanel = UiPanel('Adjust Mount')	
		panel = self.directionDialog.directionPanel
		panel.directionWidget = panel.addAltAzDirection()
		panel.directionWidget.update(alt, az, Settings.getInstance().platesolver['direction_indicator_polar_align'])
		panel.errorWidget = panel.addLineEdit('Pointing Error', editable=False)
		panel.errorWidget.setText('%0.3f arcmin' % (math.sqrt(alt * alt + az * az) * 60.0))
		panel.msgWidget = panel.addTextBox('Pointing error less than 2 arcmins is best for Astrophotography', 55)

		panel.ok = panel.addButton('Adjustment Completed')
		panel.ok.clicked.connect(self.buttonDirectionOkPressed)

		self.directionDialogLayout = QVBoxLayout()
		self.directionDialogLayout.addWidget(panel)
		self.directionDialog.setLayout(self.directionDialogLayout)

		self.directionDialog.exec()
		

	def buttonPANextPressed(self, checked):
		if self.widgetPANext.text() == 'Cancel':
			self.camera.polarAlignCancel()
		else:
			self.widgetPANext.setText('Cancel')
			self.camera.polarAlign()


	def buttonDisplayChartPressed(self):
		self.calcAnnotationStars(self.camera.lastFitFile)
		if self.starLookup is not None:
			self.displayExposureChart(self.camera.lastFitFile)
		if self.plateSolveDialog is not None:
			self.plateSolveDialog.accept()
			self.plateSolveDialog = None
			self.starLookup = None


	def buttonOverlayMagnitudesPressed(self):
		self.calcAnnotationStars(self.camera.lastFitFile)
		if self.starLookup is not None:
			self.camera.annotationStars = self.annotationStars
			self.camera.updateDisplayOptions()
		if self.plateSolveDialog is not None:
			self.plateSolveDialog.accept()
			self.plateSolveDialog = None
			self.starLookup = None

	
	# OPERATIONS

	def setEnabledUi(self, enable):
		self.widgetTask.setEnabled(enable)
		self.widgetFrameRate.setEnabled(enable)
		self.widgetExposure.setEnabled(enable)
		self.widgetNumSubs.setEnabled(enable)
		self.widgetJobName.setEnabled(enable)
		if self.settings_mount['goto_capable']:
			self.widgetDither.setEnabled(enable)
		self.widgetFullSkySolve.setEnabled(enable)
		self.widgetPlateSolve.setEnabled(enable)
		

	def PANextStepEnabled(self):
		self.widgetPANext.setEnabled(True)

	def buttonPlateSolveSyncOnlyPressed(self):
		if self.plateSolveDialog is not None:
			self.camera.syncLastPlateSolve()
			self.plateSolveDialog.accept()
			self.plateSolveDialog = None


	def buttonPlateSolveSyncGotoPressed(self):
		if self.plateSolveDialog is not None:
			self.camera.syncLastPlateSolve()
			self.camera.gotoObjectRaDec()
			self.plateSolveDialog.accept()
			self.plateSolveDialog = None


	def buttonPlateSolveOkPressed(self):
		if self.plateSolveDialog is not None:
			self.plateSolveDialog.accept()
			self.plateSolveDialog = None


	def buttonPlateSolveCancelPressed(self):
		if self.plateSolveDialog is not None:
			self.camera.solveFieldCancel()
			self.plateSolveDialog.reject()
			self.plateSolveDialog = None
			self.starLookup = None


	def buttonDirectionOkPressed(self):
		if self.directionDialog is not None:
			self.directionDialog.accept()
			self.directionDialog = None


	def switchModeTo(self, text):
		self.widgetTask.setCurrentText(text)
		self.comboBoxTaskChanged(text)


	def calcAnnotationStars(self, fits_fname):
		# Read WCS file
		f_basename = os.path.splitext(os.path.basename(fits_fname))[0]
		f_dirname = os.path.dirname(fits_fname)
		wcsFile = f_dirname + '/astrometry_tmp/' + f_basename + '.wcs'

		self.starLookup = StarLookup()
		try:
			self.annotationStars = self.starLookup.findStarsInFits(wcsFile = wcsFile, magLimit = Settings.getInstance().general['annotation_mag'])
		except FileNotFoundError:
			QMessageBox.critical(self, ' ', 'Star Catalogs Not Found!', QMessageBox.Ok)
			self.starLookup = None
			

	def displayExposureChart(self, fits_fname):
		stars, bkg_mean, bkg_median, bkg_stddev  = self.starLookup.calculateStarMetricsForFits(fitsFile = fits_fname, stars = self.annotationStars, radiusPixels = 5, sensorSaturationValue = 1023)

		print('Mag,PeakSensor')
		stars.sort(key=lambda x: x.mag_g, reverse=False)
		for star in stars:
			if hasattr(star, 'peakSensor'):
				print('%0.2f,%0.1f' % (star.mag_g, star.peakSensor))
			#else:
			#       print('No star detected')
		print('Analyzed stars:', len(stars))


		print('bkg_mean: %0.2f%%' % bkg_mean)
		print('bkg_median: %0.2f%%' % bkg_median)
		print('bkg_stddev: %0.2f%%' % bkg_stddev)

		self.dialogExposureChart = UiDialogPanel('Exposure Analysis', UiPanelExposureChart, args = {'camera': self, 'stars': stars, 'bkg_mean': bkg_mean, 'bkg_median': bkg_median, 'bkg_stddev': bkg_stddev, 'fits_fname': fits_fname }, parent = self)
