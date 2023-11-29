from UiPanel import UiPanel
from UiDialogPanel import UiDialogPanel



class UiPanelMetadata(UiPanel):
	# Initializes and displays a Panel

	PANEL_WIDTH = 700
	TEXT_BOX_WIDTH = PANEL_WIDTH - 20
	TEXT_BOX_HEIGHT = 700

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.panel		= panel

		self.widgetMetadata	= self.addTextBox(args['metadata'])
		self.widgetOk		= self.addButton('OK', True)

		self.setFixedWidth(self.PANEL_WIDTH)
		self.widgetMetadata.setFixedSize(self.TEXT_BOX_WIDTH, self.TEXT_BOX_HEIGHT)
		#self.setColumnWidth(1, self.TEXT_BOX_WIDTH)
		

	def registerCallbacks(self):
		self.widgetOk.clicked.connect(self.buttonOkPressed)

	
	# CALLBACKS

	def buttonOkPressed(self):
		self.panel.acceptDialog()
