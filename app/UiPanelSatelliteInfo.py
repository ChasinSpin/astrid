from UiPanel import UiPanel
from settings import Settings
from spacetrack import SpaceTrackClient
from datetime import datetime



class UiPanelSatelliteInfo(UiPanel):
	# Initializes and displays a Panel


	TEXT_BOX_WIDTH	= 600
	TEXT_BOX_HEIGHT	= 100


	def __init__(self, title, panel, args):
		super().__init__(title)
		self.panel		= panel

		satelliteName = args['satelliteName']

		satellites = Settings.getInstance().satellites['satellites']
		satellite = None
		for s in satellites:
			if s['name'] == satelliteName:
				satellite = s
				break

		self.widgetName			= self.addLineEdit('Object Name', editable=False);	self.widgetName.setText(satellite['name'])

		self.noradCatId			= satellite['norad_cat_id'] 
		self.widgetNoradCatId		= self.addLineEdit('NORAD Catalogue Number', editable=False);	self.widgetNoradCatId.setText(self.noradCatId)

		self.widgetDownloaded		= self.addLineEdit('Downloaded', editable=False);	self.widgetDownloaded.setText(satellite['downloaded'])
		self.widgetTleLine1		= self.addLineEdit('TLE Line 1', editable=False);	self.widgetTleLine1.setText(satellite['tle_line1'])
		self.widgetTleLine2		= self.addLineEdit('TLE Line 2', editable=False);	self.widgetTleLine2.setText(satellite['tle_line2'])


		self.widgetUpdateTLE	= self.addButton('Update Orbit Prediction')
		self.widgetOK		= self.addButton('OK')

		self.setColumnWidth(1, 300)


	def registerCallbacks(self):
		self.widgetUpdateTLE.clicked.connect(self.buttonUpdateTLEPressed)
		self.widgetOK.clicked.connect(self.buttonOKPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		self.panel.acceptDialog()


	def buttonUpdateTLEPressed(self):
		# Get TLEs
		now = datetime.utcnow()
		stserver = Settings.getInstance().spacetrack
		spacetrack = SpaceTrackClient(stserver['spacetrack_login'], stserver['spacetrack_password'])
		tles = spacetrack.gp(norad_cat_id=[int(self.noradCatId)], format='tle')
		spacetrack.close()

		if tles is not None and len(tles) != 0:
			tles = tles.splitlines()
		else:
			QMessageBox.warning(self, ' ', 'Failed to download TLE !')
			return False

		print(tles)

		# Add the satellite
		now = now.strftime('%Y-%m-%d %H:%M:%S')
		satelliteObjects = Settings.getInstance().satellites['satellites']
	
		for s in satelliteObjects:
			if int(s['norad_cat_id']) == int(self.noradCatId):
				s['tle_line1'] = tles[0]
				s['tle_line2'] = tles[1]
				s['downloaded'] = now

		Settings.getInstance().writeSubsetting('satellites')

		self.panel.acceptDialog()


	# OPERATIONS
