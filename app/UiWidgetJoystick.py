from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QComboBox, QMessageBox


AUTO_REPEAT_INITIAL_MS	= 1000
AUTO_REPEAT_INTERVAL_MS	= 500

class UiWidgetJoystick(QWidget):

	def __init__(self, camera):
		super().__init__()

		self.camera		= camera

		self.buttonUp		= QToolButton()
		self.buttonDown		= QToolButton()
		self.buttonLeft		= QToolButton()
		self.buttonRight	= QToolButton()

		allButtons = [self.buttonUp, self.buttonDown, self.buttonLeft, self.buttonRight]

		self.buttonUp.setArrowType(Qt.UpArrow)
		self.buttonDown.setArrowType(Qt.DownArrow)
		self.buttonLeft.setArrowType(Qt.LeftArrow)
		self.buttonRight.setArrowType(Qt.RightArrow)

		for button in allButtons:
			#button.setAutoRepeat(True)
			#button.setAutoRepeatDelay(AUTO_REPEAT_INITIAL_MS)	# Delay in ms before auto-repeat kicks in
			#button.setAutoRepeatInterval(AUTO_REPEAT_INTERVAL_MS)	# Length of auto repeat
			#button.setFixedSize(40,40)

			# IMPORTANT: Documentation says, icons can only be shrunk not grown, so this doesn't work, set the icon to a bigger on
			button.setIconSize(QSize(40,40))

		slewRateList = self.camera.indi.telescope.getSlewRateList()
		if len(slewRateList) > 0:
			self.comboBoxSpeed	= QComboBox()
			self.comboBoxSpeed.addItems(self.camera.indi.telescope.getSlewRateList())
			self.comboBoxSpeed.setCurrentIndex(self.camera.indi.telescope.getSlewRateIndex())
			self.comboBoxSpeed.setObjectName('comboBoxSpeed')
			#self.comboBoxSpeed.setFixedSize(40,40)
		else:
			self.comboBoxSpeed = None

		self.layout = QGridLayout()

		self.layout.addWidget(self.buttonUp, 0, 1, Qt.AlignCenter)
		self.layout.addWidget(self.buttonDown, 2, 1, Qt.AlignCenter)
		self.layout.addWidget(self.buttonLeft, 1, 0, Qt.AlignRight)
		self.layout.addWidget(self.buttonRight, 1, 2, Qt.AlignLeft)
		if self.comboBoxSpeed is not None:
			self.layout.addWidget(self.comboBoxSpeed, 1, 1, Qt.AlignCenter)

		self.setLayout(self.layout)
		
		self.__registerCallbacks()


	def __registerCallbacks(self):
		self.buttonUp.pressed.connect(self.buttonUpPressed)
		self.buttonUp.released.connect(self.buttonUpReleased)

		self.buttonDown.pressed.connect(self.buttonDownPressed)
		self.buttonDown.released.connect(self.buttonDownReleased)

		self.buttonLeft.pressed.connect(self.buttonLeftPressed)
		self.buttonLeft.released.connect(self.buttonLeftReleased)

		self.buttonRight.pressed.connect(self.buttonRightPressed)
		self.buttonRight.released.connect(self.buttonRightReleased)

		if self.comboBoxSpeed is not None:
			self.comboBoxSpeed.currentTextChanged.connect(self.comboBoxSpeedChanged)
		

        # CALLBACKS

	def buttonUpPressed(self):
		if self.camera.mountCanMove(isParkedReturnFalse=True):
			self.camera.indi.telescope.setManualMotion(1, 0)

	def buttonDownPressed(self):
		if self.camera.mountCanMove(isParkedReturnFalse=True):
			self.camera.indi.telescope.setManualMotion(-1, 0)

	def buttonLeftPressed(self):
		if self.camera.mountCanMove(isParkedReturnFalse=True):
			self.camera.indi.telescope.setManualMotion(0, 1)

	def buttonRightPressed(self):
		if self.camera.mountCanMove(isParkedReturnFalse=True):
			self.camera.indi.telescope.setManualMotion(0, -1)

	def buttonUpReleased(self):
		self.camera.indi.telescope.setManualMotion(0, 0)

	def buttonDownReleased(self):
		self.camera.indi.telescope.setManualMotion(0, 0)

	def buttonLeftReleased(self):
		self.camera.indi.telescope.setManualMotion(0, 0)

	def buttonRightReleased(self):
		self.camera.indi.telescope.setManualMotion(0, 0)

	def comboBoxSpeedChanged(self, text):
		self.camera.indi.telescope.setSlewRate(text)
