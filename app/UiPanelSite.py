from UiPanel import UiPanel
from PyQt5.QtCore import Qt, QTimer
from otestamper import OteStamper
from astsite import AstSite
from settings import Settings
from datetime import datetime


class UiPanelSite(UiPanel):
	# Initializes and displays a Panel
		
	FIXES = ['No GPS Packets', 'Not available', '2D Fix', '3D Fix']

	def __init__(self, title, panel, camera):
		super().__init__(title)
		self.camera			= camera
		self.panel			= panel
		self.widgetSiteName		= self.addLineEdit('Site Name', editable=False)
		self.widgetSiteLatitude		= self.addLineEdit('Site Latitude', editable=False)
		self.widgetSiteLongitude	= self.addLineEdit('Site Longitude', editable=False)
		self.widgetSiteAltitude		= self.addLineEdit('Site Altitude', editable=False)

		self.widgetGpsLatitude		= self.addLineEdit('GPS Latitude', editable=False)
		self.widgetGpsLongitude		= self.addLineEdit('GPS Longitude', editable=False)
		self.widgetGpsAltitude		= self.addLineEdit('GPS Altitude', editable=False)
		self.widgetGpsPDOP		= self.addLineEdit('GPS Acc. (PDOP)', editable=False)
		self.widgetGpsHDOP		= self.addLineEdit('GPS Acc. (HDOP)', editable=False)
		self.widgetGpsVDOP		= self.addLineEdit('GPS Acc. (VDOP)', editable=False)
		self.widgetGpsFix		= self.addLineEdit('GPS Fix', editable=False)

		self.widgetDifference		= self.addLineEdit('Diff. Site/GPS', editable=False)

		self.widgetUpdate		= self.addButton('Update Site and Mount')
		self.widgetCancel		= self.addButton('Cancel')

		self.setColumnWidth(1, 120)

		self.updateTimer = QTimer()
		self.updateTimer.timeout.connect(self.__updateTimer)
		self.updateTimer.setInterval(500)
		self.updateTimer.start()


	def registerCallbacks(self):
		self.widgetUpdate.clicked.connect(self.buttonUpdatePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def buttonUpdatePressed(self):
		self.updateTimer.stop()
		self.updateTimer = None

		status = OteStamper.getInstance().status

		settings = Settings.getInstance()
		site = settings.site

		if site is not None and status is not None:
			if not 'name' in site:
				site['name']	= 'Local'
			site['latitude']	= status['latitude']
			site['longitude']	= status['longitude']
			site['altitude']	= status['altitude']

			settings.writeSubsetting('site')

			AstSite.set(site['name'], site['latitude'], site['longitude'], site['altitude'])
			self.camera.indi.telescope.setSite(AstSite.lat, AstSite.lon, AstSite.alt)
			self.camera.indi.telescope.setTime(datetime.utcnow(), Settings.getInstance().mount['local_offset'])
		
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.updateTimer.stop()
		self.updateTimer = None
		self.panel.cancelDialog()


	def __updateTimer(self):
		status = OteStamper.getInstance().status
		self.widgetSiteName.setText(AstSite.name)
		self.widgetSiteLatitude.setText('%0.6f°' % AstSite.lat)
		self.widgetSiteLongitude.setText('%0.6f°' % AstSite.lon)
		self.widgetSiteAltitude.setText('%0.2fm' % AstSite.alt)

		self.widgetGpsLatitude.setText('%0.6f°' % status['latitude'])
		self.widgetGpsLongitude.setText('%0.6f°' % status['longitude'])
		self.widgetGpsAltitude.setText('%0.2fm' % status['altitude'])
		self.widgetGpsPDOP.setText(str(status['pdop']))
		self.widgetGpsHDOP.setText(str(status['hdop']))
		self.widgetGpsVDOP.setText(str(status['vdop']))
		self.widgetGpsFix.setText(UiPanelSite.FIXES[status['fix']])

		self.widgetDifference.setText('%0.2fm' % AstSite.distanceFromGps(status['latitude'], status['longitude']))


	# OPERATIONS
