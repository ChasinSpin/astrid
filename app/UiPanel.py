from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox, QPushButton, QLineEdit, QDateTimeEdit, QTextEdit, QGridLayout, QProgressBar, QTabWidget, QListWidget, QStatusBar
from PyQt5.QtGui import QValidator, QDoubleValidator, QIntValidator, QPalette, QColor, QPixmap
from UiWidgetHMSDMS import UiWidgetHMSDMS
from UiValidators import DoubleValidator, IntValidator
from UiStatusButton import UiStatusButton
from UiStatusLabel import UiStatusLabel
from UiWidgetJoystick import UiWidgetJoystick
from UiWidgetDirection import UiWidgetDirection
from UiWidgetOpencv import UiWidgetOpencv
from UiWidgetPlayerControls import UiWidgetPlayerControls
from UiWidgetChart import UiWidgetChart



class UiPanel(QWidget):
	# Initializes and displays a Panel

	def __init__(self, title, statusLabel=False):
		super().__init__()

		self.rowIndex = 0

		if statusLabel:
			self.titleLabel = UiStatusLabel(title)
		else:
			self.titleLabel = QLabel(title)

		self.frame = QFrame()
		self.frame.setObjectName('framePanel')
		self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

		self.layoutPanel = QVBoxLayout()
		self.layoutPanel.setSpacing(0)
		self.layoutPanel.setContentsMargins(0, 0, 0, 0)
		self.layoutPanel.addWidget(self.titleLabel, 0, Qt.AlignTop)
		self.layoutPanel.addWidget(self.frame, 1, Qt.AlignTop)

		self.layout = QGridLayout()
		self.frame.setLayout(self.layout)
		self.setLayout(self.layoutPanel)


	def __find_row_for_widget(self, widget: QWidget):
		idx = self.layout.indexOf(widget)
		if idx == -1:
			raise ValueError('Widget not found')
		(row, col, rowSpan, colSpan) = self.layout.getItemPosition(idx)
		return row


	def setColumnWidth(self, column, width):
		#self.layout.setColumnMinimumWidth(column, width) - This doesn't really work reliably, using this instead...
		for row in range(self.layout.rowCount()):
			layoutItem = self.layout.itemAtPosition(row, column)
			if layoutItem is not None:
				widget = layoutItem.widget()
				if widget is not None:
					idx = self.layout.indexOf(widget)
					if idx == -1:
						raise ValueError('Widget not found')
					(row, col, rowSpan, colSpan) = self.layout.getItemPosition(idx)
					if colSpan == 1:
						widget.setFixedWidth(width)


	def showWidget(self, widget: QWidget):
		row = self.__find_row_for_widget(widget)
		for col in range(self.layout.columnCount()):
			self.layout.itemAtPosition(row, col).widget().show()


	def hideWidget(self, widget: QWidget):
		row = self.__find_row_for_widget(widget)
		for col in range(self.layout.columnCount()):
			self.layout.itemAtPosition(row, col).widget().hide()


	def addComboBox(self, title: str, options: [str]) -> QComboBox:
		label = QLabel(title)

		comboBox = QComboBox()
		comboBox.addItems(options)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, Qt.AlignLeft)
		self.layout.addWidget(comboBox, self.rowIndex, 1, 1, 1, Qt.AlignLeft)

		self.rowIndex += 1
		return comboBox

	
	def addCheckBox(self, title: str) -> QCheckBox:
		label = QLabel(title)

		checkBox = QCheckBox()

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, Qt.AlignLeft)
		self.layout.addWidget(checkBox, self.rowIndex, 1, 1, 1, Qt.AlignLeft)

		self.rowIndex += 1
		return checkBox


	def addLabelButton(self, title: str, buttonTitle: str) -> QPushButton:
		label = QLabel(title)

		button = QPushButton(buttonTitle)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, Qt.AlignLeft)
		self.layout.addWidget(button, self.rowIndex, 1, 1, 1, Qt.AlignCenter)

		self.rowIndex += 1
		return button


	def addButton(self, buttonTitle: str, fullWidth = True, checkable = False) -> QPushButton:
		button = QPushButton(buttonTitle)
		alignment = Qt.AlignCenter
		if fullWidth:
			alignment = Qt.AlignVCenter
		if checkable:
			button.setCheckable(True)
		self.layout.addWidget(button, self.rowIndex, 0, 1, 2, alignment)
		self.rowIndex += 1
		return button


	def addStatusButton(self, buttonTitle: str, fullWidth = True, checkable = False) -> UiStatusButton:
		button = UiStatusButton(buttonTitle)
		alignment = Qt.AlignCenter
		if fullWidth:
			alignment = Qt.AlignVCenter
		if checkable:
			button.setCheckable(True)
		self.layout.addWidget(button, self.rowIndex, 0, 1, 2, alignment)
		self.rowIndex += 1
		return button


	def addLabel(self, title: str) -> QLabel:
		label = QLabel(title)
		self.layout.addWidget(label, self.rowIndex, 0, 1, 2, alignment=Qt.AlignLeft)
		self.rowIndex += 1
		return label


	def addLineEdit(self, title: str, editable = True) -> QLineEdit:
		label = QLabel(title)
		lineEdit = QLineEdit()

		if not editable:
			lineEdit.setReadOnly(True)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(lineEdit, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))

		self.rowIndex += 1
		return lineEdit


	def addLineEditDouble(self, title: str, bottom: float, top: float, decimalPlaces: int, editable = True) -> QLineEdit:
		lineEdit = self.addLineEdit(title, editable)
		lineEdit.setValidator(DoubleValidator(bottom, top, decimalPlaces, lineEdit))
		return lineEdit
		

	def addLineEditInt(self, title: str, bottom: int, top: int, editable = True) -> QLineEdit:
		lineEdit = self.addLineEdit(title, editable)
		lineEdit.setValidator(IntValidator(bottom, top, lineEdit))
		return lineEdit


	def addDateTimeEdit(self, title: str, qdatetime: QDateTime = QDateTime.currentDateTime(), editable = True) -> QDateTimeEdit:
		label = QLabel(title)
		dateTimeEdit = QDateTimeEdit()
		dateTimeEdit.setDateTime(qdatetime)
		dateTimeEdit.setDisplayFormat('yyyy-MM-dd hh:mm:ss')

		if not editable:
			dateTimeEdit.setEnabled(False)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(dateTimeEdit, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		dateTimeEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))

		self.rowIndex += 1
		return dateTimeEdit


	def addTextEdit(self, title: str, placeholder: str) -> QTextEdit:
		label = QLabel(title)
		textEdit = QTextEdit()
		textEdit.setPlaceholderText(placeholder)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(textEdit, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		#lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))

		self.rowIndex += 1
		return textEdit


	def addTextBox(self, text: str, height = None) -> QTextEdit:
		textEdit = QTextEdit()
		textEdit.setText(text)
		textEdit.setReadOnly(True)

		self.layout.addWidget(textEdit, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		#textEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))
		if height is not None:
			textEdit.setFixedHeight(height)

		self.rowIndex += 1
		return textEdit


	def addCoordHMS(self, title: str, editable = True) -> QLineEdit:
		label = QLabel(title)
		coordEdit = UiWidgetHMSDMS('hms')

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(coordEdit, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		self.rowIndex += 1
		return coordEdit


	def addCoordDMS(self, title: str, editable = True) -> QLineEdit:
		label = QLabel(title)
		coordEdit = UiWidgetHMSDMS('dms')

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(coordEdit, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		self.rowIndex += 1
		return coordEdit


	def addJoystick(self, camera) -> UiWidgetJoystick:
		joystick = UiWidgetJoystick(camera)
		alignment = Qt.AlignCenter | Qt.AlignVCenter
		self.layout.addWidget(joystick, self.rowIndex, 0, 1, 2, alignment)
		self.rowIndex += 1
		return joystick


	def addAltAzDirection(self):
		direction = UiWidgetDirection()
		alignment = Qt.AlignCenter | Qt.AlignVCenter
		self.layout.addWidget(direction, self.rowIndex, 0, 1, 2, alignment)
		self.rowIndex += 1
		return  direction


	def addSpacer(self):
		label = QLabel('')
		self.layout.addWidget(label, self.rowIndex, 0, 1, 2, alignment=Qt.AlignLeft)

		self.rowIndex += 1
		return label


	def addProgressBar(self, title: str):
		label = QLabel(title)

		progress = QProgressBar()
		palette = progress.palette()
		palette.setColor(QPalette.Highlight, QColor('green'))
		progress.setPalette(palette)
		progress.setMaximumSize(250, 20)
		progress.setVisible(False)

		progress.setRange(0, 100)
		progress.setValue(0)

		self.layout.addWidget(label, self.rowIndex, 0, 1, 1, alignment=Qt.AlignLeft)
		self.layout.addWidget(progress, self.rowIndex, 1, 1, 1, alignment=Qt.AlignLeft)

		#lineEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))

		self.rowIndex += 1
		return progress


	def addTabs(self, titles: [str], widgets: [QWidget]):
		tabs = QTabWidget()

		for i in range(len(widgets)):
			tabs.addTab(widgets[i], titles[i])

		self.layout.addWidget(tabs, self.rowIndex, 0, 1, 2, alignment=Qt.AlignLeft)
		
		self.rowIndex += 1
		return tabs


	def addList(self, items: [str]):
		wlist = QListWidget()
	
		wlist.addItems(items)

		self.layout.addWidget(wlist, self.rowIndex, 0, 1, 2, alignment=Qt.AlignLeft)

		self.rowIndex += 1
		return wlist


	def addTextBox(self, text: str, height = None) -> QTextEdit:
		textEdit = QTextEdit()
		textEdit.setText(text)
		textEdit.setReadOnly(True)

		self.layout.addWidget(textEdit, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		#textEdit.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))
		if height is not None:
			textEdit.setFixedHeight(height)

		self.rowIndex += 1
		return textEdit


	def addOpencv(self, width, height) -> UiWidgetOpencv:
		opencv = UiWidgetOpencv(width, height)

		self.layout.addWidget(opencv, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		self.rowIndex += 1
		return opencv


	def addPlayerControls(self, callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame, callback_togglePlay, callback_setFrameNum) -> UiWidgetPlayerControls:
		controls = UiWidgetPlayerControls(callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame, callback_togglePlay, callback_setFrameNum)

		self.layout.addWidget(controls, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		self.rowIndex += 1
		return controls


	def addSearchXMLPredictions(self, width, height, callback_buttonCancelPressed):
		# Import defined here instead of at top to prevent circular import
		from UiWidgetSearchXMLPredictions import UiWidgetSearchXMLPredictions

		searchXMLPredictions = UiWidgetSearchXMLPredictions(width, height, callback_buttonCancelPressed)

		self.layout.addWidget(searchXMLPredictions, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		self.rowIndex += 1
		return searchXMLPredictions


	def addStatusBar(self):
		statusBar = QStatusBar()
	
		self.layout.addWidget(statusBar, self.rowIndex, 0, 1, 2, alignment=Qt.AlignLeft)

		self.rowIndex += 1
		return statusBar


	def addChart(self, width, height) -> UiWidgetOpencv:
		chart = UiWidgetChart(width, height)

		self.layout.addWidget(chart, self.rowIndex, 0, 1, 2, alignment=Qt.AlignCenter)

		self.rowIndex += 1
		return chart
