from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QComboBox, QMessageBox



class UiWidgetPlayerControls(QWidget):

	def __init__(self, callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame):
		super().__init__()

		self.callback_firstFrame = callback_firstFrame
		self.callback_lastFrame = callback_lastFrame
		self.callback_prevFrame = callback_prevFrame
		self.callback_nextFrame = callback_nextFrame

		self.buttonFirstFrame	= QToolButton()
		self.buttonLastFrame	= QToolButton()
		self.buttonPrevFrame	= QToolButton()
		self.buttonNextFrame	= QToolButton()

		self.buttonFirstFrame.setText('<<')
		self.buttonLastFrame.setText('>>')
		self.buttonPrevFrame.setText('<')
		self.buttonNextFrame.setText('>')

		self.buttonFirstFrame.setFixedSize(40,40)
		self.buttonLastFrame.setFixedSize(40,40)
		self.buttonPrevFrame.setFixedSize(40,40)
		self.buttonNextFrame.setFixedSize(40,40)
		
		self.buttonFirstFrame.setIconSize(QSize(40,40))
		self.buttonLastFrame.setIconSize(QSize(40,40))
		self.buttonPrevFrame.setIconSize(QSize(40,40))
		self.buttonNextFrame.setIconSize(QSize(40,40))

		self.layout = QGridLayout()

		self.layout.addWidget(self.buttonFirstFrame, 0, 0, Qt.AlignCenter)
		self.layout.addWidget(self.buttonPrevFrame, 0, 1, Qt.AlignCenter)
		self.layout.addWidget(self.buttonNextFrame, 0, 2, Qt.AlignRight)
		self.layout.addWidget(self.buttonLastFrame, 0, 3, Qt.AlignLeft)

		self.setLayout(self.layout)
		
		self.__registerCallbacks()


	def __registerCallbacks(self):
		self.buttonFirstFrame.pressed.connect(self.buttonFirstFramePressed)
		self.buttonLastFrame.pressed.connect(self.buttonLastFramePressed)
		self.buttonPrevFrame.pressed.connect(self.buttonPrevFramePressed)
		self.buttonNextFrame.pressed.connect(self.buttonNextFramePressed)

		#self.buttonUp.released.connect(self.buttonUpReleased)
		

        # CALLBACKS

	def buttonFirstFramePressed(self):
		self.callback_firstFrame()

	def buttonLastFramePressed(self):
		self.callback_lastFrame()

	def buttonPrevFramePressed(self):
		self.callback_prevFrame()

	def buttonNextFramePressed(self):
		self.callback_nextFrame()
