from processlogger import ProcessLogger
from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox
from settings import Settings



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

		for o in self.all_objects:
			self.items.append(o['name'])

		self.items.reverse()

		self.widgetList		= self.addList(self.items)
		self.widgetList.setFixedHeight(400)

		self.widgetEdit		= self.addButton('Edit', True)
		self.widgetDelete	= self.addButton('Delete', True)
		self.widgetSelect	= self.addButton('Select', True)

		self.widgetEdit.setEnabled(False)
		self.widgetDelete.setEnabled(False)
		self.widgetSelect.setEnabled(False)

		self.widgetCancel	= self.addButton('Cancel', True)

		self.setColumnWidth(1, 170)
		

	def registerCallbacks(self):
		self.widgetList.itemSelectionChanged.connect(self.listItemChanged)
		self.widgetEdit.clicked.connect(self.buttonEditPressed)
		self.widgetDelete.clicked.connect(self.buttonDeletePressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)
		self.widgetSelect.clicked.connect(self.buttonSelectPressed)

	
	# CALLBACKS


	def listItemChanged(self):
		self.widgetEdit.setEnabled(True)
		self.widgetDelete.setEnabled(True)
		self.widgetSelect.setEnabled(True)


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


	def buttonCancelPressed(self):
		self.panel.cancelDialog()


	def buttonSelectPressed(self):
		item = self.selectedItem()

		self.panel.acceptDialog()

		if item is not None:
			self.selectListCallback(item)
	

	# OPERATIONS

	def selectedItem(self):
		selectedItems = self.widgetList.selectedItems()
		if len(selectedItems) == 1:
			row = self.widgetList.row(selectedItems[0])
			return self.items[row]
		else:
			return None
