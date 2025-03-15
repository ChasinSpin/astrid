from UiPanel import UiPanel
from PyQt5.QtCore import Qt



class UiPanelConnectFailedIndi(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, camera):
		super().__init__(title)

		self.camera = camera

		self.panel		= panel
		self.widgetMessage	= self.addTextBox('Troubleshooting:\n    1. Verify USB cable is connected from ASTRID to the mount and focuser(if used)\n    2. Check mount and focuser(if used) are powered on\n    3. Try to connect again (e.g. SkyWatcher mounts)\n    4. Verify both Focuser(if not set to simulator) AND mount are connected')
		self.widgetMessage.setFixedWidth(600)
		self.widgetOK		= self.addButton('Try Again')
		self.widgetSimulate	= self.addButton('Simulate Mount')
		self.widgetCancel	= self.addButton('Cancel')


	def registerCallbacks(self):
		self.widgetOK.clicked.connect(self.buttonOKPressed)
		self.widgetSimulate.clicked.connect(self.buttonSimulatePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		self.panel.acceptDialog()


	def buttonSimulatePressed(self):
		self.camera.simulateMount()
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()
		self.camera.exitNow()


	# OPERATIONS
