from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QComboBox, QMessageBox


AUTO_REPEAT_INITIAL_MS	= 1000
AUTO_REPEAT_INTERVAL_MS	= 500

class UiWidgetFocuser(QWidget):

	def __init__(self, buttonUpCallback, buttonDownCallback, buttonSpeedCallback):
		super().__init__()

		self.buttonUpCallback	= buttonUpCallback
		self.buttonDownCallback	= buttonDownCallback
		self.buttonSpeedCallback= buttonSpeedCallback

		self.buttonUp		= QToolButton()
		self.buttonDown		= QToolButton()

		allButtons = [self.buttonUp, self.buttonDown]

		self.buttonUp.setArrowType(Qt.UpArrow)
		self.buttonDown.setArrowType(Qt.DownArrow)

		for button in allButtons:
			button.setAutoRepeat(True)
			button.setAutoRepeatDelay(AUTO_REPEAT_INITIAL_MS)	# Delay in ms before auto-repeat kicks in
			button.setAutoRepeatInterval(AUTO_REPEAT_INTERVAL_MS)	# Length of auto repeat
			#button.setFixedSize(40,40)

			# IMPORTANT: Documentation says, icons can only be shrunk not grown, so this doesn't work, set the icon to a bigger on
			button.setIconSize(QSize(40,40))

		self.comboBoxSpeed	= QComboBox()
		self.comboBoxSpeed.addItems(['Coarse', 'Fine'])
		self.comboBoxSpeed.setCurrentIndex(0)
		self.comboBoxSpeed.setObjectName('comboBoxSpeed')
		#self.comboBoxSpeed.setFixedSize(40,40)

		self.layout = QGridLayout()

		self.layout.addWidget(self.buttonUp, 0, 1, Qt.AlignCenter)
		self.layout.addWidget(self.buttonDown, 2, 1, Qt.AlignCenter)
		if self.comboBoxSpeed is not None:
			self.layout.addWidget(self.comboBoxSpeed, 1, 1, Qt.AlignCenter)

		self.setLayout(self.layout)
		
		self.__registerCallbacks()


	def __registerCallbacks(self):
		self.buttonUp.pressed.connect(self.buttonUpPressed)
		self.buttonUp.released.connect(self.buttonUpReleased)

		self.buttonDown.pressed.connect(self.buttonDownPressed)
		self.buttonDown.released.connect(self.buttonDownReleased)

		if self.comboBoxSpeed is not None:
			self.comboBoxSpeed.currentTextChanged.connect(self.comboBoxSpeedChanged)
		

        # CALLBACKS

	def buttonUpPressed(self):
		self.buttonUpCallback()

	def buttonDownPressed(self):
		self.buttonDownCallback()

	def buttonUpReleased(self):
		pass

	def buttonDownReleased(self):
		pass

	def comboBoxSpeedChanged(self, text):
		self.buttonSpeedCallback(text)
