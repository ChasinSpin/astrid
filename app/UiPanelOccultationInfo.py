from UiPanel import UiPanel
from settings import Settings
from astcoord import AstCoord
from owcloud import OWCloud
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl



class UiPanelOccultationInfo(UiPanel):
	# Initializes and displays a Panel


	TEXT_BOX_WIDTH	= 600
	TEXT_BOX_HEIGHT	= 100


	def __init__(self, title, panel, args):
		super().__init__(title)
		self.panel		= panel
		occultationName		= args['occultationName']
		self.radec_format	= Settings.getInstance().camera['radec_format']

		occultations = Settings.getInstance().occultations['occultations']
		occultation = None
		for o in occultations:
			if o['name'] == occultationName:
				occultation = o
				break

		hasOccelmnt = False
		if len(occultation['occelmnt'].keys()) > 0:
			hasOccelmnt = True

		self.owcloudUrl = None
		if 'owcloudurl' in occultation.keys():
			self.owcloudUrl = occultation['owcloudurl']

		self.widgetName			= self.addLineEdit('Object Name', editable=False);	self.widgetName.setText(occultation['name'])

		coords = AstCoord.from360Deg(occultation['ra'], occultation['dec'], 'icrs')
		if self.radec_format == 'hour':
			self.widgetRA           = self.addLineEditDouble('RA', 0.0, 23.9999999999, 10, editable=False)
			self.widgetDEC          = self.addLineEditDouble('DEC', -90.0, 90.0, 10, editable=False)
			radec = coords.raDec24Deg('icrs')
			self.widgetRA.setText(str(radec[0]))
			self.widgetDEC.setText(str(radec[1]))
		elif self.radec_format == 'hmsdms':
			self.widgetRA  = self.addLineEdit('RA (HMS)', editable=False)
			self.widgetDEC = self.addLineEdit('DEC (DMS)', editable=False)
			radec = coords.raDecHMSStr('icrs')
			self.widgetRA.setText(radec[0])
			self.widgetDEC.setText(radec[1])
		elif self.radec_format == 'deg':
			self.widgetRA           = self.addLineEditDouble('RA', 0.0, 359.9999999999, 10, editable=False)
			self.widgetDEC          = self.addLineEditDouble('DEC', -90.0, 90.0, 10, editable=False)
			radec = coords.raDec360Deg('icrs')
			self.widgetRA.setText(str(radec[0]))
			self.widgetDEC.setText(str(radec[1]))

		self.widgetEventTime		= self.addLineEdit('Event Center Time', editable=False);	self.widgetEventTime.setText(occultation['event_time'] + ' UTC')
		self.widgetStartTime		= self.addLineEdit('Event Start Time', editable=False);		self.widgetStartTime.setText(occultation['start_time'] + ' UTC')
		self.widgetEndTime		= self.addLineEdit('Event End Time', editable=False);		self.widgetEndTime.setText(occultation['end_time'] + ' UTC')
		self.widgetEventDuration	= self.addLineEdit('Max Duration', editable=False);		self.widgetEventDuration.setText(str(occultation['event_duration']) + ' s')
		self.widgetEventUncertainty	= self.addLineEdit('Error in time', editable=False);		self.widgetEventUncertainty.setText(str(occultation['event_uncertainty']) + ' s')

		if hasOccelmnt:
			occelmnt = occultation['occelmnt']['Occultations']['Event']
			
			star	= occelmnt['Star'].split(',')
			object	= occelmnt['Object'].split(',')
			errors	= occelmnt['Errors'].split(',')

			self.widgetSpacer1			= self.addSpacer()
			self.widgetStarName			= self.addLineEdit('Star Name', editable=False);			self.widgetStarName.setText(star[0])
			self.widgetStarMagnitude		= self.addLineEdit('Star Magnitude(Visual)', editable=False);		self.widgetStarMagnitude.setText(star[4])
			self.widgetStarDiameter			= self.addLineEdit('Star Diameter', editable=False);			self.widgetStarDiameter.setText(star[6] + ' mas')
			self.widgetStarMagDrop			= self.addLineEdit('Star Magnitude Drop', editable=False);		self.widgetStarMagDrop.setText(star[11])

			self.widgetSpacer2			= self.addSpacer()
			self.widgetAsteroidMag			= self.addLineEdit('Asteroid Magnitude', editable=False);		self.widgetAsteroidMag.setText(object[2])
			self.widgetAsteroidDiameter		= self.addLineEdit('Asteroid Diameter', editable=False);		self.widgetAsteroidDiameter.setText(object[3] + ' km ±' + object[10])
			self.widgetAsteroidDistance		= self.addLineEdit('Asteroid Distance', editable=False);		self.widgetAsteroidDistance.setText(object[4] + ' au')

			self.widgetSpacer3		= self.addSpacer()
			self.widgetPathUncertainty	= self.addLineEdit('Path Uncertainty', editable=False);				self.widgetPathUncertainty.setText('%0.3f' % (float(errors[0])-1.0) + ' path widths')
			self.widgetErrorBasis		= self.addLineEdit('Error Basis', editable=False);				self.widgetErrorBasis.setText(errors[5])

			self.widgetSpacer4		= self.addSpacer()
		else:
			self.widgetNote = self.addTextBox('Occultation was manually entered and contains no occelmnt data.\n\nTo get additional information about the star etc., import your sites from OWCloud or enter occelmnt data when manually adding events.', height = 40)
			self.widgetNote.setFixedSize(UiPanelOccultationInfo.TEXT_BOX_WIDTH, UiPanelOccultationInfo.TEXT_BOX_HEIGHT)

		if self.owcloudUrl is not None:
			self.widgetOpenOWCloud		= self.addButton('Open on OWCloud')
		self.widgetOK		= self.addButton('OK')

		self.setColumnWidth(1, 300)


	def registerCallbacks(self):
		if self.owcloudUrl is not None:
			self.widgetOpenOWCloud.clicked.connect(self.buttonOpenOnOWCloudPressed)
			
		self.widgetOK.clicked.connect(self.buttonOKPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		self.panel.acceptDialog()


	def buttonOpenOnOWCloudPressed(self):
		QDesktopServices.openUrl(QUrl(self.owcloudUrl))



	# OPERATIONS
