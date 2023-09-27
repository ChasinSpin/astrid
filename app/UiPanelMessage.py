from UiPanel import UiPanel
from PyQt5.QtCore import Qt



class UiPanelMessage(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, args: dict):
		super().__init__(title)

		self.panel		= panel
		msg			= args['msg']
		buttonText		= args['buttonText']
		self.widgetMessage	= self.addTextBox(msg)
		self.widgetMessage.setFixedWidth(600)
		self.widgetOK		= self.addButton(buttonText)


	def registerCallbacks(self):
		self.widgetOK.clicked.connect(self.buttonOKPressed)


	# CALLBACKS	

	def buttonOKPressed(self):
		self.panel.acceptDialog()


	# OPERATIONS
