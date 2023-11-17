import os
import subprocess
from UiPanel import UiPanel
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from settings import Settings
from StarCatalogExtract import StarCatalogExtract



class UiPanelDisplay2(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 2')

		self.camera = camera
		self.widgetExpAnalysis	= self.addButton('Exposure Analysis')


	def registerCallbacks(self):
		self.widgetExpAnalysis.clicked.connect(self.buttonExpAnalysis)
		


	# CALLBACKS

	def buttonExpAnalysis(self):
		self.camera.annotationStars = None
		self.camera.updateDisplayOptions()

		starCatalogExtract = StarCatalogExtract()
		if starCatalogExtract.checkAndExtract():
			self.camera.ui.panelTask.buttonPlateSolvePressed(True, expAnalysis = True)
       

	# OPERATIONS
