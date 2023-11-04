from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractButton
from datetime import datetime, timezone
from UiWidgetSearchXMLPredictionsControls import UiWidgetSearchXMLPredictionsControls
from OccelmntXMLSearch import OccelmntXMLSearch, OccelmntEvent



# Runs OccelmntXMLSearch via a seperate thread

class OccelmntXMLSearchThread(QThread):
	searchFoundEvent	= pyqtSignal(OccelmntEvent)
	searchStatus		= pyqtSignal(str)
	searchComplete		= pyqtSignal()


	def __init__(self, xml_fname, lat, lon, alt, startDate, endDate, starMagLimit, magDropLimit):
		super(QThread, self).__init__()

		self.xml_fname		= xml_fname
		self.lat		= lat
		self.lon		= lon
		self.alt		= alt
		self.startDate		= startDate
		self.endDate		= endDate
		self.starMagLimit	= starMagLimit
		self.magDropLimit	= magDropLimit

		self.search	= None


	def __statusUpdate(self, txt):
		self.searchStatus.emit(txt)


	def abort(self):
		if self.search is not None:
			self.search.abort = True


	def __foundEvent(self, event):
		self.searchFoundEvent.emit(event)
		

	def run(self):
		self.searchStatus.emit('Counting events in: %s, please wait...' % self.xml_fname)

		self.search = OccelmntXMLSearch(self.xml_fname)
		self.searchStatus.emit('Total Events: %d' % self.search.total_events)

		self.search.searchEvents(self.lat, self.lon, self.alt, self.startDate, self.endDate, self.starMagLimit, self.magDropLimit, self.__statusUpdate, self.__foundEvent)

		self.searchStatus.emit('Search Complete. Found %d events that matched criteria, from a total of %d events' % (len(self.search.found_events), self.search.total_events))

		self.searchComplete.emit()

		search = None


class UiWidgetSearchXMLPredictions(QWidget):

	WIDTH_TABLE_DIFFERENCE	= 56
	HEIGHT_TABLE_DIFFERENCE	= 320

	def __init__(self, width, height, callback_buttonCancelPressed):
		super().__init__()

		self.events = []
		self.thread = None
		self.callback_buttonCancelPressed = callback_buttonCancelPressed

		self.setupTableWidget(width - UiWidgetSearchXMLPredictions.WIDTH_TABLE_DIFFERENCE, height - UiWidgetSearchXMLPredictions.HEIGHT_TABLE_DIFFERENCE)
		self.controlsWidget = UiWidgetSearchXMLPredictionsControls(self.buttonCancelPressed, self.buttonClearPressed, self.buttonExportPressed, self.buttonSearchPressed)

		self.layout = QGridLayout()
		self.layout.addWidget(self.controlsWidget,	0, 0, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.tableWidget,		1, 0, 1, 1, Qt.AlignCenter)
		self.layout.setRowMinimumHeight(1, height)
		self.layout.setColumnMinimumWidth(0, width)
		self.setLayout(self.layout)


	def setupTableWidget(self, width, height):
		# Create dummy event, so we can get the keys for the headers
		dummy = OccelmntEvent('', datetime.utcnow(), '', '', 0.0, 0.0, 0.0, 0.0, 0.0)

		self.tableWidget = QTableWidget()

		self.tableWidget.setSortingEnabled(True)
		self.tableWidget.setRowCount(1)
		self.tableWidget.setColumnCount(dummy.columns())
		self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
		self.tableWidget.horizontalHeader().setSortIndicator(1, Qt.AscendingOrder)

		dummy_keys = dummy.keys()
		for i in range(dummy.columns()):
			self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(dummy_keys[i]))

		self.tableWidget.horizontalHeader().setStretchLastSection(True) 
		self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 

		self.tableWidget.setFixedSize(width, height)


	def addOccelmntEventToTable(self, event):
		event_keys = event.keys()

		self.tableWidget.setSortingEnabled(False)	# Sorting must be disabled as we add rows, otherwise table gets scrambled

		rowCount = self.tableWidget.rowCount()
		if len(self.events) == 0:
			insertRow = 0
		else:
			self.tableWidget.setRowCount(rowCount + 1)
			insertRow = rowCount

		for r in range(event.columns()):
			item = QTableWidgetItem()
			item.setData(Qt.EditRole, event.getValueForEvent(event_keys[r]))
			self.tableWidget.setItem(insertRow, r, item)

		self.events.append(event)

		self.tableWidget.setSortingEnabled(True)	# Reenabling sorting


	# Callbacks

	def buttonCancelPressed(self):
		if self.thread is not None:
			self.thread.abort()
			self.thread = None
		self.callback_buttonCancelPressed()
	

	def buttonClearPressed(self):
		self.tableWidget.setSortingEnabled(False)

		self.tableWidget.clearContents()
		self.tableWidget.setRowCount(1)
		self.events = []

		self.tableWidget.setSortingEnabled(True)
	

	def buttonExportPressed(self):
		pass
	

	def buttonSearchPressed(self):
		self.startSearch()


	# Operations

	def __searchFoundEvent(self, event):
		self.addOccelmntEventToTable(event)

	def __searchStatus(self, txt):
		self.controlsWidget.widgetStatusBar.showMessage(txt)


	def __searchComplete(self):
		self.thread = None


	def startSearch(self):

		startDate = datetime.strptime(self.controlsWidget.widgetStartDate.dateTime().toString('yyyy-MM-dd hh:mm:ss'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
		endDate   = datetime.strptime(self.controlsWidget.widgetEndDate.dateTime().toString('yyyy-MM-dd hh:mm:ss'), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
		self.thread = OccelmntXMLSearchThread(	'predictions/' + self.controlsWidget.widgetOccelmntXML.currentText(),	\
							float(self.controlsWidget.widgetLatitude.text()),			\
							float(self.controlsWidget.widgetLongitude.text()),			\
							float(self.controlsWidget.widgetAltitude.text()),			\
							startDate,								\
							endDate,								\
							float(self.controlsWidget.widgetStarMag.text()),			\
							float(self.controlsWidget.widgetMagDrop.text())
						     )

		self.thread.searchFoundEvent.connect(self.__searchFoundEvent)
		self.thread.searchStatus.connect(self.__searchStatus)
		self.thread.searchComplete.connect(self.__searchComplete)
		self.thread.finished.connect(self.thread.deleteLater)
		self.thread.start()
