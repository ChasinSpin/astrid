from UiPanel import UiPanel
from PyQt5.QtCore import Qt



class UiPanelConnectFailedIndi(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, camera):
		super().__init__(title)

		self.camera = camera

		self.panel		= panel
		self.widgetMessage	= self.addTextBox('Troubleshooting:\n    1. Verify USB cable is connected from ASTRID to the mount\n    2. Check mount is powered on\n    3. Try the next USB device (below)')
		self.widgetMessage.setFixedWidth(600)
		self.widgetTryNext	= self.addButton('Try Next USB Device')
		self.widgetOK		= self.addButton('Try Again')
		self.widgetSimulate	= self.addButton('Simulate Mount')
		self.widgetCancel	= self.addButton('Cancel')


	def registerCallbacks(self):
		self.widgetTryNext.clicked.connect(self.buttonTryNextPressed)
		self.widgetOK.clicked.connect(self.buttonOKPressed)
		self.widgetSimulate.clicked.connect(self.buttonSimulatePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def buttonTryNextPressed(self):
		self.camera.nextUsbTty()
		self.panel.acceptDialog()


	def buttonOKPressed(self):
		self.panel.acceptDialog()


	def buttonSimulatePressed(self):
		self.camera.simulateMount()
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()
		self.camera.exitNow()


	# OPERATIONS
