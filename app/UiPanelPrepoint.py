from UiPanel import UiPanel
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from settings import Settings
from astcoord import AstCoord
from datetime import datetime, timedelta
from astutils import AstUtils


PREPOINT_FIELD_WIDTH = 180


class UiPanelPrepoint(UiPanel):

	def __init__(self, title, panel, args):
		super().__init__(title)
		self.panel		= panel
		self.object		= args['object']
		self.camera		= args['camera']

		self.gotoCapable	= Settings.getInstance().mount['goto_capable']
		self.trackingCapable	= Settings.getInstance().mount['tracking_capable']

		# If we're tracking capable switch it off so we don't confuse the prepoint calculations
		if self.trackingCapable:
			self.camera.indi.telescope.tracking(False)
		
		if self.gotoCapable:
			self.future_secs = 10
		else:
			self.future_secs = 15

		self.widgetRA           = self.addLineEdit('Prepoint RA', editable = False)
		self.widgetDEC          = self.addLineEdit('Prepoint DEC', editable = False)
		self.widgetPrepointTime = self.addLineEdit('Prepoint Time', editable = False)
	
		self.calcPrepoint()

		direction_indicator_platesolve = Settings.getInstance().platesolver['direction_indicator_platesolve']
		if direction_indicator_platesolve != 'None':
			self.widgetAltAzDirection = self.addAltAzDirection()
			self.hideWidget(self.widgetAltAzDirection)
		else:
			self.widgetAltAzDirection = None

		self.widgetFOVError = self.addLineEdit('Pos Error (%FOV)', editable = False)
		self.hideWidget(self.widgetFOVError)

		self.widgetFOVSize = self.addLineEdit('FOV Size', editable = False)
		self.hideWidget(self.widgetFOVSize)

		self.widgetMaxDrift = self.addLineEdit('Drift Time Thru FOV', editable = False)
		self.hideWidget(self.widgetMaxDrift)

		if self.gotoCapable:
			self.widgetGoto	= self.addButton('Goto')
			self.hideWidget(self.widgetGoto)
		else:
			self.widgetGoto = None

		self.widgetPhotoProc	= self.addButton('Photo, Solve and Sync')

		self.widgetExit	= self.addButton('Exit Prepoint')
		self.setColumnWidth(1, PREPOINT_FIELD_WIDTH)


	def registerCallbacks(self):
		self.widgetPhotoProc.clicked.connect(self.buttonPhotoProcPressed)
		if self.widgetGoto is not None:
			self.widgetGoto.clicked.connect(self.buttonGotoPressed)
		self.widgetExit.clicked.connect(self.buttonExitPressed)


	# CALLBACKS	

	def buttonGotoPressed(self):
		self.widgetGoto.setEnabled(False)
		self.camera.gotoNoTracking(self.prepoint, self.widgetGoto)


	def buttonPhotoProcPressed(self):
		if self.widgetPhotoProc.text() == 'Photo, Solve and Sync':
			self.calcPrepoint()
			self.widgetPhotoProc.setText('Cancel')
			if self.widgetAltAzDirection is not None:
				self.widgetAltAzDirection.setEnabled(False)
			self.camera.takePhotoSolveSync(self, self.prepoint)
		else:
			self.camera.takePhotoSolveSyncCancel()
			self.photoProcFailed()


	def buttonExitPressed(self):
		self.panel.cancelDialog()


	# OPERATIONS

	def calcPrepoint(self):
		self.prepointTime = datetime.utcnow() + timedelta(seconds = self.future_secs)
		#self.prepointTime = datetime(2023, 9, 13, 5, 15, 00)

		self.widgetPrepointTime.setText(self.prepointTime.strftime('%Y-%m-%dT%H:%M:%SZ'))

		if self.trackingCapable:
			event_time = self.object['start_time']
		else:
			event_time = self.object['event_time']

		dte_event_time = datetime.strptime(event_time, '%Y-%m-%dT%H:%M:%S')

		targetCoords = AstCoord.from360Deg(self.object['ra'], self.object['dec'], 'icrs')

		print('Target (ICRS): %s @ %s' % (targetCoords.raDecHMSStr('icrs'), dte_event_time.strftime('%Y-%m-%dT%H:%M:%SZ')))

		prepointCoords = targetCoords.prepointCoords(targetInFOVTime = dte_event_time,  prepointTime = self.prepointTime)

		print('Prepoint Position (ICRS): %s @ %s' % (prepointCoords.raDecHMSStr('icrs'), self.prepointTime.strftime('%Y-%m-%dT%H:%M:%SZ')))

		self.prepoint = prepointCoords

		# Calculate drift in arcseconds per second
		print('Time1:', self.prepointTime)
		print('Time2:', dte_event_time)
		self.delta_time =  (dte_event_time - self.prepointTime).total_seconds()
		self.delta_time %= AstCoord.SIDEREAL_DAY_LENGTH * 3600.0			# Wrap araound per sidereal day
		self.angular_separation = self.prepoint.angular_separation(targetCoords)	# Degrees
		self.drift_speed = self.angular_separation/self.delta_time
		print('angular seperation: %0.7fdeg  drift speed: %0.7fdeg/sec  delta time: %dsecs' % (self.angular_separation, self.drift_speed, self.delta_time))
	
		(ra, dec) = self.prepoint.raDecStrForSettingFormat('icrs')
		self.widgetRA.setText(ra)
		self.widgetDEC.setText(dec)


	def photoProcComplete(self, position, field_size, altAzPlateSolve):
		if self.widgetAltAzDirection is not None:
			direction_indicator_platesolve = Settings.getInstance().platesolver['direction_indicator_platesolve']
			delta = AstUtils.calculatePlateSolveTargetDelta(position, altAzPlateSolve, self.prepoint)
			altAzDelta = delta[0]
			raDecDelta = delta[1]
			self.widgetAltAzDirection.update(raDecDelta[0], raDecDelta[1], altAzDelta[0], altAzDelta[1], direction_indicator_platesolve, True)
			self.showWidget(self.widgetAltAzDirection)
			self.widgetAltAzDirection.setEnabled(True)

			maxAltAzDelta = max(abs(altAzDelta[0]), abs(altAzDelta[1]))

			field_size2 = field_size[:-1]	# remove the degree sign
			field_size2 = field_size2.split('x')
			field_size2 = (float(field_size2[0]), float(field_size2[1]))
			field_size2 = (abs(field_size2[0]), abs(field_size2[1]))
			minFieldSize = min(field_size2[0], field_size2[1])

			fovErrorPercent = (maxAltAzDelta / minFieldSize) * 100.0
			self.widgetFOVError.setText('%0.1f%%' % fovErrorPercent)

			self.widgetFOVSize.setText(str(field_size))

			# Calculate the time it takes to drift through the fields of view in minutes
			driftFOV = ((field_size2[0] / self.drift_speed) / 60.0, (field_size2[1] / self.drift_speed) / 60.0)
			self.widgetMaxDrift.setText('%0.2fx%0.2f min(s)' % (driftFOV[0], driftFOV[1]))

		self.widgetPhotoProc.setText('Photo, Solve and Sync')
		self.showWidget(self.widgetFOVError)
		self.showWidget(self.widgetFOVSize)
		self.showWidget(self.widgetMaxDrift)
		if self.widgetGoto is not None:
			self.showWidget(self.widgetGoto)


	def photoProcFailed(self):
		self.widgetPhotoProc.setText('Photo, Solve and Sync')
		self.hideWidget(self.widgetFOVError)
		self.hideWidget(self.widgetFOVSize)
		self.hideWidget(self.widgetMaxDrift)
		self.hideWidget(self.widgetAltAzDirection)
		if self.widgetGoto is not None:
			self.hideWidget(self.widgetGoto)
		self.panel.dialog.adjustSize()
		self.adjustSize()
