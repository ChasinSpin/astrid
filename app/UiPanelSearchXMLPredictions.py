from UiPanel import UiPanel
from settings import Settings
from astcoord import AstCoord
from owcloud import OWCloud
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl



class UiPanelSearchXMLPredictions(UiPanel):
	# Initializes and displays a Panel


	WIDTH	= 1200
	HEIGHT	= 750

	def __init__(self, title, panel, args):
		super().__init__(title)
		self.panel			= panel

		self.widgetSearchPredictions	= self.addSearchXMLPredictions(UiPanelSearchXMLPredictions.WIDTH, UiPanelSearchXMLPredictions.HEIGHT, self.buttonCancelPressed);
		self.setFixedSize(UiPanelSearchXMLPredictions.WIDTH, UiPanelSearchXMLPredictions.HEIGHT)


	def registerCallbacks(self):
		pass


	# CALLBACKS	

	def buttonCancelPressed(self):
		self.panel.acceptDialog()



	# OPERATIONS
