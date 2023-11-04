from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractButton
from datetime import datetime
from UiWidgetSearchXMLPredictionsControls import UiWidgetSearchXMLPredictionsControls
from OccelmntXMLSearch import OccelmntXMLSearch



# Runs OccelmntXMLSearch via a seperate thread

class OccelmntXMLSearchThread(QThread):
	searchFoundEvent	= pyqtSignal(str)
	searchStatus		= pyqtSignal(str)
	searchComplete		= pyqtSignal(str)


	def __init__(self, xml_fname, lat, lon, alt):
		super(QThread, self).__init__()

		self.xml_fname	= xml_fname
		self.lat	= lat
		self.lon	= lon
		self.alt	= alt

		self.search	= None


	def __statusUpdate(self, txt):
		self.searchStatus.emit(txt)


	def abort(self):
		if self.search is not None:
			self.search.abort = True
		

	def run(self):
		self.searchStatus.emit('Counting events in: %s, please wait...' % self.xml_fname)
		self.search = OccelmntXMLSearch(self.xml_fname)
		self.searchStatus.emit('Total Events: %s' % self.search.total_events)

		self.search.searchEvents(self.lat, self.lon, self.alt, self.__statusUpdate)

		self.searchComplete.emit('Search Completed')

		search = None



class OccelmntEvent():

	def __init__(self, object: str, eventTime: str, objectId: str, starId: str, duration: float, starMag: float, magDrop: float, pathWidthError: float, distance: float):
		# Creating the formating for the keys in details below, None = str (nothing to do)
		self.format =	[					\
				None,		# object		\
				None,		# time			\
				None,		# object id		\
				None,		# star id		\
				'%0.2f',	# duration 		\
				'%0.2f',	# star mag.		\
				'%0.2f',	# mag drop.		\
				'%0.3f',	# path width error	\
				'%0.2f',	# distance(km)		\
				]

		self.details = {					\
				'Object': object,			\
				'Event Time': eventTime,		\
				'Object Id': objectId,			\
				'Star Id': starId,			\
				'Duration(s)': duration,		\
				'Star Mag.': starMag, 			\
				'Mag. Drop': magDrop,			\
				'Path Width Error': pathWidthError,	\
				'Distance(km)': distance		\
				}	

		if len(self.format) != len(self.keys()):
			raise ValueError('length self.format != self.details, must be one format for every key')


	def formatPropertyAsStr(self, key):
		""" Returns key formatted as string """
		ind = self.keys().index(key)
		if self.format[ind] is None:
			return self.details[key]
		else:
			return self.format[ind] % (self.details[key])


	def columns(self):
		return len(self.details.keys())


	def keys(self):
		return list(self.details.keys())


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
		self.tableWidget.setRowCount(0)
		self.tableWidget.setColumnCount(dummy.columns())
		self.tableWidget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

		dummy_keys = dummy.keys()
		for i in range(dummy.columns()):
			self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(dummy_keys[i]))

		self.events = []
		testTime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
		self.events.append(OccelmntEvent('Althaea', 	'2024-01-14 21:41:38', '119', 'TYC  635-01094-1', 5.88, 11.97, 1.35, 0.039, 248.9208))
		self.events.append(OccelmntEvent('Liberatrix', '2024-01-11 04:31:48', '125', 'UCAC4 535-022303', 3.71, 13.42, 0.69, 0.310, 88.5124))
		self.events.append(OccelmntEvent('Elsa',	'2024-01-27 09:23:52', '182', 'TYC 1239-00081-1', 4.14, 10.53, 2.31, 0.067, 122.3693))

		dummy = OccelmntEvent('', datetime.utcnow(), '', '', 0.0, 0.0, 0.0, 0.0, 0.0)

		for i in range(len(self.events)):
			self.addOccelmntEventToTable(self.events[i])

		self.tableWidget.horizontalHeader().setStretchLastSection(True) 
		self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) 

		self.tableWidget.setFixedSize(width, height)


	def addOccelmntEventToTable(self, event):
		event_keys = event.keys()

		self.tableWidget.setSortingEnabled(False)	# Sorting must be disabled as we add rows, otherwise table gets scrambled

		rowCount = self.tableWidget.rowCount()
		self.tableWidget.setRowCount(rowCount + 1)

		for r in range(event.columns()):
			self.tableWidget.setItem(rowCount, r, QTableWidgetItem(event.formatPropertyAsStr(event_keys[r]))) 

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
		pass

	def __searchStatus(self, txt):
		self.controlsWidget.widgetStatusBar.showMessage(txt)


	def __searchComplete(self, txt):
		self.controlsWidget.widgetStatusBar.showMessage('Search Complete')
		self.thread = None


	def startSearch(self):
		self.thread = OccelmntXMLSearchThread('predictions/' + self.controlsWidget.widgetOccelmntXML.currentText(), float(self.controlsWidget.widgetLatitude.text()), float(self.controlsWidget.widgetLongitude.text()), float(self.controlsWidget.widgetAltitude.text()))
		self.thread.searchFoundEvent.connect(self.__searchFoundEvent)
		self.thread.searchStatus.connect(self.__searchStatus)
		self.thread.searchComplete.connect(self.__searchComplete)
		self.thread.finished.connect(self.thread.deleteLater)
		self.thread.start()
