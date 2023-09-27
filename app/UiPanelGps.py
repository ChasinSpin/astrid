from UiPanel import UiPanel
from PyQt5.QtCore import Qt, QTimer
from otestamper import OteStamper



class UiPanelGps(UiPanel):
	# Initializes and displays a Panel

	FIXES = ['No GPS Packets', 'Not available', '2D Fix', '3D Fix']


	def __init__(self, title, panel):
		super().__init__(title)
		self.panel		= panel
		self.widgetSatellites	= self.addLineEdit('Satellites', editable=False)
		self.widgetFix		= self.addLineEdit('Fix', editable=False)
		self.widgetOK		= self.addButton('OK')

		self.setColumnWidth(1, 100)

		self.updateTimer = QTimer()
		self.updateTimer.timeout.connect(self.__updateTimer)
		self.updateTimer.setInterval(500)
		self.updateTimer.start()


	def registerCallbacks(self):
		self.widgetOK.clicked.connect(self.buttonOKPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		self.updateTimer.stop()
		self.updateTimer = None
		self.panel.cancelDialog()


	def __updateTimer(self):
		status = OteStamper.getInstance().status
		self.widgetSatellites.setText(str(status['numSatellites']))
		self.widgetFix.setText(UiPanelGps.FIXES[status['fix']])


	# OPERATIONS
