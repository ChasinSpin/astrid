from UiPanel import UiPanel
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime



class UiPanelSatelliteGetTime(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.panel		= panel

		self.widgetEventTime	= self.addDateTimeEdit('Event Time(UTC)')

		self.widgetContinue	= self.addButton('Continue', True)

		self.widgetCancel	= self.addButton('Cancel', True)

		#self.setColumnWidth(1, 170)


	def registerCallbacks(self):
		self.widgetContinue.clicked.connect(self.buttonContinuePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)

	
	# CALLBACKS

	def buttonContinuePressed(self):
		self.event_time = self.widgetEventTime.dateTime().toString('yyyy-MM-dd hh:mm:ss')
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()
	

	# OPERATIONS
