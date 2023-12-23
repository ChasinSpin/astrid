import os
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QDateEdit, QPushButton, QStatusBar
from datetime import datetime
from astsite import AstSite
from UiValidators import DoubleValidator
from settings import Settings



class UiWidgetSearchXMLPredictionsControls(QWidget):

	def __init__(self, callback_buttonCancelPressed, callback_buttonClearPressed, callback_buttonExportPressed, callback_buttonSearchPressed):
		super().__init__()

		self.layout = QGridLayout()

		self.layout.setRowMinimumHeight(2, 10)
		self.layout.setRowMinimumHeight(5, 10)
		self.layout.setRowMinimumHeight(8, 10)
		self.layout.setColumnMinimumWidth(3, 80)
		self.layout.setColumnMinimumWidth(6, 80)


		self.widgetOccelmntXML		= QComboBox()
		self.widgetStartDate		= QDateEdit()
		self.widgetEndDate		= QDateEdit()
		self.widgetLatitude		= QLineEdit()
		self.widgetLongitude		= QLineEdit()
		self.widgetAltitude		= QLineEdit()
		self.widgetStarMag		= QLineEdit()
		self.widgetMagDrop		= QLineEdit()
		self.widgetStarAltitude		= QLineEdit()
		self.widgetSunAltitude		= QLineEdit()
		self.widgetDistance		= QLineEdit()
		self.buttonCancel		= QPushButton('Cancel')
		self.buttonClear		= QPushButton('Clear Results')
		self.buttonExport		= QPushButton('Export as CSV')
		self.buttonSearch		= QPushButton('Search')
		self.widgetStatusBar		= QStatusBar()

		self.widgetOccelmntXML.setObjectName('comboBoxOccelmntXML')
		self.widgetStartDate.setDisplayFormat('yyyy-MM-dd')
		self.widgetEndDate.setDisplayFormat('yyyy-MM-dd')
		self.widgetLatitude.setValidator(DoubleValidator(-90.0, +90.0, 7, self.widgetLatitude))
		self.widgetLongitude.setValidator(DoubleValidator(-180.0, 180.0, 7, self.widgetLongitude))
		self.widgetAltitude.setValidator(DoubleValidator(-20.0, 20000.0, 1, self.widgetAltitude))
		self.widgetStarMag.setValidator(DoubleValidator(0.0, 30.0, 1, self.widgetStarMag))
		self.widgetMagDrop.setValidator(DoubleValidator(0.0, 30.0, 1, self.widgetMagDrop))
		self.widgetStarAltitude.setValidator(DoubleValidator(0.0, 90.0, 1, self.widgetStarAltitude))
		self.widgetSunAltitude.setValidator(DoubleValidator(-20.0, 0.0, 1, self.widgetSunAltitude))
		self.widgetDistance.setValidator(DoubleValidator(0.0, 20000.0, 1, self.widgetDistance))

		self.layout.addWidget(QLabel('Occelment XML'),			0, 0, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetOccelmntXML, 			1, 0, 1, 2, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Start Date (UTC)'),		3, 0, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetStartDate, 			4, 0, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('End Date (UTC)'),			3, 1, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetEndDate, 			4, 1, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Latitude (deg)'),			6, 0, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetLatitude,			7, 0, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Longitude (deg)'),		6, 1, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetLongitude, 			7, 1, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Altitude (m)'),			6, 2, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetAltitude, 			7, 2, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Limit Star Magnitude'),		0, 4, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetStarMag, 			1, 4, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Limit Event Magnitude Drop '),	3, 4, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetMagDrop, 			4, 4, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Limit Star Altitude (deg)'),	6, 4, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetStarAltitude, 			7, 4, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Limit Sun Altitude (deg)'),	0, 5, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetSunAltitude, 			1, 5, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(QLabel('Limit Distance (km)'),		3, 5, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.widgetDistance, 			4, 5, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(self.buttonClear, 			1, 7, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.buttonExport, 			4, 7, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.buttonCancel, 			7, 6, 1, 1, Qt.AlignVCenter)
		self.layout.addWidget(self.buttonSearch, 			7, 7, 1, 1, Qt.AlignVCenter)

		self.layout.addWidget(self.widgetStatusBar, 			8, 0, 1, 8, Qt.AlignVCenter)


		# Add the list of files to the combo box
		filenames = os.listdir(Settings.getInstance().predictions_folder)
		options = []
		for fname in filenames:
			if fname.endswith('.xml'):
				options.append(fname)
		options.sort()
		self.widgetOccelmntXML.addItems(options)

		startDate = QDate.currentDate()
		self.widgetStartDate.setDate(startDate)
		self.widgetEndDate.setDate(startDate.addMonths(1))

		self.widgetLatitude.setText(str(AstSite.lat))
		self.widgetLongitude.setText(str(AstSite.lon))
		self.widgetAltitude.setText(str(AstSite.alt))
		self.widgetStarMag.setText('14.0')
		self.widgetMagDrop.setText('0.1')
		self.widgetStarAltitude.setText('10.0')
		self.widgetSunAltitude.setText('-15.0')
		self.widgetDistance.setText('300.0')

		self.setLayout(self.layout)

		self.buttonCancel.clicked.connect(callback_buttonCancelPressed)
		self.buttonClear.clicked.connect(callback_buttonClearPressed)
		self.buttonExport.clicked.connect(callback_buttonExportPressed)
		self.buttonSearch.clicked.connect(callback_buttonSearchPressed)
