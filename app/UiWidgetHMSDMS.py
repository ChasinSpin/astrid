from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout 
from UiValidators import DoubleValidator, IntValidator

class UiWidgetHMSDMS(QWidget):

	def __init__(self, hmsdms, editable = True):
		super().__init__()

		self.hmsdms		= hmsdms

		self.hoursDegEdit	= QLineEdit()
		self.minsEdit		= QLineEdit()
		self.secsEdit		= QLineEdit()
		if self.hmsdms == 'hms':
			self.hoursDegLabel = QLabel('h')
		else:
			self.hoursDegLabel = QLabel('d')
		self.minsLabel		= QLabel('m')
		self.secsLabel		= QLabel('s')

		self.hoursDegEdit.setFixedWidth(30)
		self.minsEdit.setFixedWidth(30)
		self.secsEdit.setFixedWidth(75)

		if not editable:
			self.hoursDegEdit.setReadOnly(True)
			self.minsEdit.setReadOnly(True)
			self.secsEdit.setReadOnly(True)
		else:
			if hmsdms == 'hms':
				self.hoursDegEdit.setValidator(IntValidator(0, 23, self.hoursDegEdit))
			else:
				self.hoursDegEdit.setValidator(IntValidator(-90, 90, self.hoursDegEdit))
			self.minsEdit.setValidator(IntValidator(0, 59, self.minsEdit))
			self.secsEdit.setValidator(DoubleValidator(0, 59.99999, 5, self.secsEdit))

		self.layout = QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)

		self.layout.addWidget(self.hoursDegEdit)
		self.layout.addWidget(self.hoursDegLabel)
		self.layout.addWidget(self.minsEdit)
		self.layout.addWidget(self.minsLabel)
		self.layout.addWidget(self.secsEdit)
		self.layout.addWidget(self.secsLabel)

		self.setLayout(self.layout)
		
		self.__registerCallbacks()


	def __registerCallbacks(self):
		self.hoursDegEdit.editingFinished.connect(self.hoursDegChanged)
		self.minsEdit.editingFinished.connect(self.minsChanged)
		self.secsEdit.editingFinished.connect(self.secsChanged)


	def hoursDegChanged(self):
		value = int(self.hoursDegEdit.text())
		self.__validateAll()


	def minsChanged(self):
		value = int(self.minsEdit.text())
		self.__validateAll()


	def secsChanged(self):
		value = float(self.secsEdit.text())
		self.__validateAll()


	def __validateAll(self):
		value = int(self.hoursDegEdit.text())
		if self.hmsdms == 'dms' and (value == -90 or value == 90):
			self.setValue(value, 0, 0.0)


	def setValue(self, hoursDeg: int, mins: int, secs:float):
		self.hoursDegEdit.setText('%02d' % hoursDeg)
		self.minsEdit.setText('%02d' % mins)
		self.secsEdit.setText('%#08.5f' % secs)


	def getValue(self) -> (int, int, float):
		return (int(self.hoursDegEdit.text()), int(self.minsEdit.text()), float(self.secsEdit.text()))
