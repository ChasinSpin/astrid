import subprocess
from UiPanel import UiPanel
from PyQt5.QtCore import Qt
from otestamper import OteStamper
from datetime import datetime



class UiPanelTiming(UiPanel):
	# Initializes and displays a Panel

	PPS = ['Not Seen', 'Seen, but not active', 'Active', 'Active']

	fixedWidth = 350

	def __init__(self, title, panel):
		super().__init__(title)
		self.panel				= panel
		self.widgetPps				= self.addLineEdit('PPS', editable=False)
		self.widgetLeapSeconds			= self.addLineEdit('Leap Seconds', editable=False)
		self.widgetLeapSecondsSource		= self.addLineEdit('Leap Seconds Source', editable=False)
		self.widgetTime				= self.addLineEdit('GPS Time', editable=False)
		self.widgetSystemGPSDeltaChrony		= self.addLineEdit('GPS/System Time Delta(s) - Chrony', editable=False)
		self.widgetSystemGPSDeltaTimestamp	= self.addLineEdit('GPS/System Time Delta(s) - Timestamp', editable=False)
		self.widgetOK				= self.addButton('OK')

		OteStamper.getInstance().setGpsTimeCallback(self.__updateTimer)

		# Get the system / GPS delta from chronyc
		process = subprocess.Popen('/usr/bin/chronyc tracking | /usr/bin/grep "System time" | /usr/bin/sed "s/NTP/GPS/" | /usr/bin/sed "s/System time     : //"', stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		process.status = process.wait()
		self.widgetSystemGPSDeltaChrony.setText(output.decode('utf-8'))

		self.setColumnWidth(1, UiPanelTiming.fixedWidth)


	def registerCallbacks(self):
		self.widgetOK.clicked.connect(self.buttonOKPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		OteStamper.getInstance().setGpsTimeCallback(None)
		self.panel.cancelDialog()


	def __updateTimer(self, status):
		self.widgetPps.setText(UiPanelTiming.PPS[status['clockStatus'] & 0x03])

		self.widgetLeapSeconds.setText(str(status['leapSeconds']))

		if  status['clockStatus'] & 0x04:
			self.widgetLeapSecondsSource.setText('GPS')
		elif  status['clockStatus'] & 0x08:
			self.widgetLeapSecondsSource.setText('Eeprom')
		elif  status['clockStatus'] & 0x10:
			self.widgetLeapSecondsSource.setText('Software')
		else:
			self.widgetLeapSecondsSource.setText('Unknown')

		try:
			dt = datetime.fromtimestamp(status['unixEpoch'])
		except OverflowError:
			self.widgetTime.setText('Unknown')
			self.widgetSystemGPSDeltaTimestamp.setText('Unknown')
		else:
			self.widgetTime.setText(dt.strftime('%Y-%m-%d %H:%M:%S'))
			self.widgetSystemGPSDeltaTimestamp.setText('GPS is %d seconds ahead of system' % status['deltaSystemTimeSecs'])


	# OPERATIONS
