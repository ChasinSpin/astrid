from astutils import AstUtils
from UiPanel import UiPanel
from settings import Settings
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMessageBox
from astropy import units as u
from astcoord import AstCoord
from astropy.coordinates import SkyCoord


class UiPanelMount(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):

		self.settings = Settings.getInstance().mount

		if self.settings['mount_is_j2000']:
			mountFrame = 'J2000'
		else:
			mountFrame = 'JNOW'

		super().__init__('Mount (%s)' % mountFrame)
		self.camera		= camera
		self.widgetName		= self.addLineEdit('Name', editable = False)
		self.widgetName.setText(self.settings['name'])
		if self.settings['goto_capable']:
			if self.settings['parkmethod'] == 'home':
				self.widgetHome		= self.addButton('Home')
			else:	
				self.widgetHome		= self.addButton('Park', checkable=True)
				self.widgetHome.setObjectName('buttonCheckable')
		if self.settings['tracking_capable']:
			self.widgetTracking	= self.addButton('Tracking', checkable=True)
			self.widgetTracking.setObjectName('buttonCheckable')
		self.widgetRA		= self.addLineEdit('Position RA', editable = False)
		self.widgetDEC		= self.addLineEdit('Position DEC', editable = False)

		if self.settings['align_axis'] == 'eq':
			self.widgetMeridian	= self.addLineEdit('Meridian', editable = False)
		else:
			self.widgetMeridian	= None

		if self.settings['tracking_capable']:
			self.trackingRateList = ['sidereal', 'solar', 'lunar', 'custom']
			self.widgetTrackingRate	= self.addComboBox('Tracking Rate', self.trackingRateList)
			self.widgetTrackingRate.setCurrentIndex(self.trackingRateList.index(self.camera.indi.telescope.getTrackMode()))
			self.widgetTrackingRate.setObjectName('comboBoxTrackingRate')

		if self.settings['goto_capable']:
			self.widgetJoystick	= self.addJoystick(camera)
			self.widgetAbortMotion	= self.addButton('STOP')

		self.upcomingMeridianFlashing = False
		self.meridianFlipTimerDivider = 0
		self.meridianMins = 0

		self.meridianFlipTimerStylesheetNormal		= AstUtils.stylesheetStrToColorScheme('border: 2px solid @colorBorderMuted;')
		self.meridianFlipTimerStylesheetUpcoming	= 'border: 2px solid #FFCC00;'
		self.meridianFlipTimerStylesheetPassed		= 'border: 2px solid #FF3333;'

		self.setColumnWidth(1, 140)


	def registerCallbacks(self):
		if self.settings['goto_capable']:
			self.widgetHome.clicked.connect(self.buttonHomePressed)
			self.widgetAbortMotion.clicked.connect(self.buttonAbortMotionPressed)
		if self.settings['tracking_capable']:
			self.widgetTracking.clicked.connect(self.buttonTrackingPressed)
			self.widgetTrackingRate.currentTextChanged.connect(self.comboBoxTrackingRateChanged)


	# CALLBACKS

	def buttonHomePressed(self):
		if self.settings['parkmethod'] == 'home':
			self.camera.indi.telescope.goHome()
		else:
			self.camera.togglePark()


	def buttonTrackingPressed(self):
		self.camera.indi.telescope.lockTrackingOff = False
		self.camera.toggleTracking()


	def buttonAbortMotionPressed(self):
		self.camera.indi.telescope.abortMotion()


	def comboBoxTrackingRateChanged(self, text):
		self.camera.indi.telescope.setTrackMode(text)


	# OPERATIONS

	def setRaDecPos(self, coord):
		(ra, dec) = coord.raDecStrForSettingFormat('icrs')

		self.widgetRA.setText(ra)
		self.widgetDEC.setText(dec)


	def startMeridianFlipTimer(self):
		if self.widgetMeridian is not None:
			self.meridianFlipTimer = QTimer()
			self.meridianFlipTimer.timeout.connect(self.__meridianFlipTimerEvent)
			self.meridianFlipTimer.setInterval(1000)
			self.meridianFlipTimer.start()


	def __meridianFlipTimerEvent(self):
		self.meridianFlipTimerDivider += 1
		if (self.meridianFlipTimerDivider % 10) == 0:
			self.camera.meridianFlipUpdate()

		if self.upcomingMeridianFlashing:
			if (self.meridianFlipTimerDivider % 2) == 0:
				self.widgetMeridian.setStyleSheet(self.meridianFlipTimerStylesheetNormal)
			else:
				if self.meridianMins < 0:
					self.widgetMeridian.setStyleSheet(self.meridianFlipTimerStylesheetPassed)
				else:
					self.widgetMeridian.setStyleSheet(self.meridianFlipTimerStylesheetUpcoming)

	def setMeridian(self, mins):
		if self.widgetMeridian is not None:
			self.meridianMins = mins
			if self.meridianMins >= 0 and self.meridianMins <= 30:
				self.upcomingMeridianFlashing = True
			self.widgetMeridian.setText(str(int(self.meridianMins)) + 'm')

	def resetUpcomingMeridianFlasher(self):
		if self.widgetMeridian is not None:
			self.upcomingMeridianFlashing = False
			self.widgetMeridian.setStyleSheet(self.meridianFlipTimerStylesheetNormal)

	def messageBoxNoPlateSolve(self):
		QMessageBox.warning(self, ' ', 'Plate solve last photo before syncing.', QMessageBox.Ok)
