import os
from processlogger import ProcessLogger
from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox
from settings import Settings
from UiDialogPanel import UiDialogPanel
from UiPanelOccultationInfo import UiPanelOccultationInfo
from UiPanelSatelliteInfo import UiPanelSatelliteInfo



class UiPanelObjectList(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()

		self.radec_format = Settings.getInstance().camera['radec_format']

		self.database		= args['database']
		self.camera		= args['camera']
		self.panel		= panel

		self.selectListCallback	= args['selectListCallback']
		self.editListCallback	= args['editListCallback']

		self.items = []
		if self.database == 'Custom':
			self.all_objects = Settings.getInstance().objects['custom_objects']
			self.db = 'objects'
		elif self.database == 'Occultations':
			self.all_objects = Settings.getInstance().occultations['occultations']
			self.db = 'occultations'
		elif self.database == 'Satellites':
			self.all_objects = Settings.getInstance().satellites['satellites']
			self.db = 'satellites'

		for o in self.all_objects:
			self.items.append(o['name'])

		self.items.reverse()

		self.widgetList		= self.addList(self.items)
		self.widgetList.setFixedHeight(350)

		if self.database == 'Satellites':
			self.widgetEdit		= None
		else:
			self.widgetEdit		= self.addButton('Edit', True)
	
		self.widgetDelete	= self.addButton('Delete', True)
		self.widgetSpacer1	= self.addSpacer()
		if self.database == 'Occultations' or self.database == 'Satellites':
			self.widgetInfo		= self.addButton('Info', True)
		else:
			self.widgetInfo		= None
		self.widgetSelect	= self.addButton('Select', True)

		if self.widgetEdit is not None:
			self.widgetEdit.setEnabled(False)
		self.widgetDelete.setEnabled(False)
		self.widgetSelect.setEnabled(False)
		if self.widgetInfo is not None:
			self.widgetInfo.setEnabled(False)

		if self.database == 'Occultations':
			self.widgetSpacer2		= self.addSpacer()
			self.widgetExportLocations	= self.addButton('Export OWCloud Locations', True)
		else:
			self.widgetExportLocations	= None

		self.widgetSpacer3	= self.addSpacer()
		self.widgetCancel	= self.addButton('Cancel', True)

		# If we have a least one item, select that one by default (this gets rid of the grayed out marker)
		if len(self.items) > 0:
			self.widgetList.setCurrentRow(0)
			self.listItemChanged()

		self.setColumnWidth(1, 300)
		

	def registerCallbacks(self):
		self.widgetList.itemSelectionChanged.connect(self.listItemChanged)
		if self.widgetEdit is not None:
			self.widgetEdit.clicked.connect(self.buttonEditPressed)
		self.widgetDelete.clicked.connect(self.buttonDeletePressed)
		if self.widgetInfo is not None:
			self.widgetInfo.clicked.connect(self.buttonInfoPressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)
		self.widgetSelect.clicked.connect(self.buttonSelectPressed)
		if self.widgetExportLocations is not None:
			self.widgetExportLocations.clicked.connect(self.buttonExportLocationsPressed)

	
	# CALLBACKS


	def listItemChanged(self):
		if self.widgetEdit is not None:
			self.widgetEdit.setEnabled(True)
		self.widgetDelete.setEnabled(True)
		self.widgetSelect.setEnabled(True)
		if self.widgetInfo is not None:
			self.widgetInfo.setEnabled(True)


	def buttonEditPressed(self):
		item = self.selectedItem()

		self.panel.acceptDialog()

		if item is not None:
			self.editListCallback(item)


	def buttonDeletePressed(self):
		item = self.selectedItem()
		if item is not None:
			ret = QMessageBox.question(self, ' ', 'Delete "%s"?' % item, QMessageBox.Yes | QMessageBox.No)
			if ret == QMessageBox.Yes:
				for o in self.all_objects:
					if o['name'] == item:
						self.all_objects.remove(o)
						Settings.getInstance().writeSubsetting(self.db)
						self.logger.info('deleted %s from %s' % (item, self.db))
						break
				self.panel.acceptDialog()


	def buttonInfoPressed(self):
		item = self.selectedItem()
		if item is not None:
			if self.database == 'Satellites':
				self.dialog = UiDialogPanel('Satellite Info', UiPanelSatelliteInfo, args = {'satelliteName': item})
			else:
				self.dialog = UiDialogPanel('Occultation Info', UiPanelOccultationInfo, args = {'occultationName': item})


	def buttonCancelPressed(self):
		self.panel.cancelDialog()


	def buttonSelectPressed(self):
		if self.database == 'Occultations' and not self.camera.ui.panelStatus.goForRecordingVideo():
			QMessageBox.critical(self, ' ', 'Status buttons must be Green to select an occultation !  Check GPS connection, update site and/or wait until signal is acquired.\n\nThis is necessary because the occultation predicted time is checked against the current location and then adjusted if necessary.\n\nPlease try again when you have a good fix!', QMessageBox.Ok)
			self.panel.cancelDialog()
			return

		item = self.selectedItem()

		self.panel.acceptDialog()

		if item is not None:
			self.selectListCallback(item)


	def buttonExportLocationsPressed(self):
		planning_folder = Settings.getInstance().astrid_drive + '/planning'
		if not os.path.isdir(planning_folder):
			os.mkdir(planning_folder)
		deployments_fname = planning_folder + '/deployments.txt'

		with open(deployments_fname, 'w') as fp:	
			for occultation in self.all_objects:
				if 'latitude' in occultation.keys() and 'longitude' in occultation.keys():
					star = occultation['occelmnt']['Occultations']['Event']['Star'].split(',')
	
					fp.write('Name: %s\r\n' % occultation['name'])
					fp.write('\tEvent Time:         %s UTC\r\n' % occultation['event_time'])
					fp.write('\tEvent Duration:     %s s\r\n'   % str(occultation['event_duration']))
					fp.write('\tStar Altitude:      %s deg\r\n' % str(occultation['star_alt']))
					fp.write('\tStar Azimuth:       %s deg\r\n' % str(occultation['star_az']))
					fp.write('\tStar Mag. V:        %s\r\n'     % star[4])
					fp.write('\tStar Mag. Drop V.:  %s\r\n'     % star[11])
					fp.write('\tLocation (iPhone):  comgooglemapsurl://maps.google.com/?q=%s,%s\r\n' % (str(occultation['latitude']), str(occultation['longitude'])))
					fp.write('\tLocation (URL):     https://maps.google.com/?q=%s,%s\r\n' % (str(occultation['latitude']), str(occultation['longitude'])))
					fp.write('\r\n')

		QMessageBox.information(self, ' ', 'Deployments written to "planning/deployments.txt" on the Astrid Drive', QMessageBox.Ok)
	

	# OPERATIONS

	def selectedItem(self):
		selectedItems = self.widgetList.selectedItems()
		if len(selectedItems) == 1:
			row = self.widgetList.row(selectedItems[0])
			return self.items[row]
		else:
			return None
