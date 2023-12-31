from PyQt5.QtCore import Qt
from UiPanel import UiPanel
from UiStatusButton import UiStatusButton
from UiStatusLabel import UiStatusLabel
from UiPanelSite import UiPanelSite
from UiPanelGps import UiPanelGps
from UiPanelTiming import UiPanelTiming
from UiPanelAcquisition import UiPanelAcquisition
from UiDialogPanel import UiDialogPanel
from PyQt5.QtCore import QTimer
from datetime import datetime


class UiPanelStatus(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Status', statusLabel=True)
		self.camera		= camera
		self.widgetSite		= self.addStatusButton('Site')
		self.widgetGps		= self.addStatusButton('GPS')
		self.widgetTiming	= self.addStatusButton('Timing')
		self.widgetAcquisition	= self.addStatusButton('Acquisition')
		self.widgetTime		= self.addLineEdit('UTC Time', editable = False)

		self.widgetSite.setStatus(UiStatusButton.STATUS_UNKNOWN)
		self.widgetGps.setStatus(UiStatusButton.STATUS_UNKNOWN)
		self.widgetTiming.setStatus(UiStatusButton.STATUS_ADEQUATE)
		self.widgetAcquisition.setStatus(UiStatusButton.STATUS_GOOD)

		self.displayedSite		= False
		self.displayedGps		= False
		self.displayedTiming		= False
		self.displayedAcquisition	= False

		self.dialog = None

		self.updateStatusLabel()

		self.updateTimer = QTimer()
		self.updateTimer.timeout.connect(self.__updateTimer)
		self.updateTimer.setInterval(500)
		self.updateTimer.start()


	def registerCallbacks(self):
		self.widgetSite.clicked.connect(self.buttonSitePressed)
		self.widgetGps.clicked.connect(self.buttonGpsPressed)
		self.widgetTiming.clicked.connect(self.buttonTimingPressed)
		self.widgetAcquisition.clicked.connect(self.buttonAcquisitionPressed)


	# CALLBACKS

	def buttonSitePressed(self):
		if self.dialog:
			self.dialog.done(0)
			self.dialog = None
		self.displayedSite ^= True
		if self.displayedSite:
			self.displayedGps		= False
			self.displayedTiming		= False
			self.displayedAcquisition	= False
			self.dialog = UiDialogPanel('Site Information', UiPanelSite, args = self.camera, parent = self.camera.ui, modal = False)

	def buttonGpsPressed(self):
		if self.dialog:
			self.dialog.done(0)
			self.dialog = None
		self.displayedGps ^= True
		if self.displayedGps:
			self.displayedSite		= False
			self.displayedTiming		= False
			self.displayedAcquisition	= False
			self.dialog = UiDialogPanel('GPS Information', UiPanelGps, parent = self.camera.ui, modal = False)

	def buttonTimingPressed(self):
		if self.dialog:
			self.dialog.done(0)
			self.dialog = None
		self.displayedTiming ^= True
		if self.displayedTiming:
			self.displayedSite		= False
			self.displayedGps		= False
			self.displayedAcquisition	= False
			self.dialog = UiDialogPanel('Timing Information', UiPanelTiming, parent = self.camera.ui, modal = False)

	def buttonAcquisitionPressed(self):
		if self.dialog:
			self.dialog.done(0)
			self.dialog = None
		self.displayedAcquisition ^= True
		if self.displayedAcquisition:
			self.displayedSite		= False
			self.displayedGps		= False
			self.displayedTiming		= False
			self.dialog = UiDialogPanel('Acquisition Information', UiPanelAcquisition, parent = self.camera.ui, modal = False)


	# OPERATIONS

	def updateStatusLabel(self):
		statuses = [UiStatusButton.STATUS_UNKNOWN, UiStatusButton.STATUS_POOR, UiStatusButton.STATUS_ADEQUATE, UiStatusButton.STATUS_GOOD]
		minStatus = statuses.index(statuses[-1])
	
		for widget in [self.widgetSite, self.widgetGps, self.widgetTiming, self.widgetAcquisition]:
			ind = statuses.index(widget.status) 
			if ind < minStatus:
				minStatus = ind

		self.titleLabel.setStatus(statuses[minStatus])


	def __updateTimer(self):
		self.widgetTime.setText(datetime.utcnow().strftime("%H:%M:%S - %b %d"))


	def goForRecordingVideo(self) -> bool:
		""" Returns True if we're a go for recording video """
		if (self.widgetSite.status == UiStatusButton.STATUS_GOOD or self.widgetSite.status == UiStatusButton.STATUS_ADEQUATE) and \
		   (self.widgetGps.status == UiStatusButton.STATUS_GOOD or self.widgetGps.status == UiStatusButton.STATUS_ADEQUATE) and \
		   (self.widgetTiming.status == UiStatusButton.STATUS_GOOD or self.widgetTiming.status == UiStatusButton.STATUS_GOOD) and \
		   (self.widgetAcquisition.status == UiStatusButton.STATUS_GOOD or self.widgetAcquisition.status == UiStatusButton.STATUS_ADEQUATE):
			return True

		return False
