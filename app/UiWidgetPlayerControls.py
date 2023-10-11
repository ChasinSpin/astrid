from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton



class UiWidgetPlayerControls(QWidget):

	FRAME_NUM_WIDTH = 70

	def __init__(self, callback_firstFrame, callback_lastFrame, callback_prevFrame, callback_nextFrame, callback_togglePlay, callback_setFrameNum):
		super().__init__()

		self.callback_firstFrame	= callback_firstFrame
		self.callback_lastFrame		= callback_lastFrame
		self.callback_prevFrame		= callback_prevFrame
		self.callback_nextFrame		= callback_nextFrame
		self.callback_togglePlay	= callback_togglePlay
		self.callback_setFrameNum	= callback_setFrameNum

		self.buttonFirstFrame	= QToolButton()
		self.buttonLastFrame	= QToolButton()
		self.buttonPrevFrame	= QToolButton()
		self.buttonNextFrame	= QToolButton()

		self.buttonFirstFrame.setText('<<')
		self.buttonLastFrame.setText('>>')
		self.buttonPrevFrame.setText('<')
		self.buttonNextFrame.setText('>')

		self.buttonFirstFrame.setObjectName('playerControls')
		self.buttonLastFrame.setObjectName('playerControls')
		self.buttonPrevFrame.setObjectName('playerControls')
		self.buttonNextFrame.setObjectName('playerControls')

		self.buttonFirstFrame.setFixedSize(40,40)
		self.buttonLastFrame.setFixedSize(40,40)
		self.buttonPrevFrame.setFixedSize(40,40)
		self.buttonNextFrame.setFixedSize(40,40)
		
		self.buttonFirstFrame.setIconSize(QSize(40,40))
		self.buttonLastFrame.setIconSize(QSize(40,40))
		self.buttonPrevFrame.setIconSize(QSize(40,40))
		self.buttonNextFrame.setIconSize(QSize(40,40))

		self.currentFrameLineEdit = QLineEdit()
		self.currentFrameLineEdit.setFixedWidth(UiWidgetPlayerControls.FRAME_NUM_WIDTH)
		self.labelOf = QLabel()
		self.labelOf.setText('of')
		self.lastFrameLineEdit = QLineEdit()
		self.lastFrameLineEdit.setReadOnly(True)
		self.lastFrameLineEdit.setFixedWidth(UiWidgetPlayerControls.FRAME_NUM_WIDTH)

		self.buttonPlayPause = QPushButton('Play')
		self.buttonPlayPause.setObjectName('playerControls')
	
		self.layout = QGridLayout()

		self.layout.addWidget(self.buttonFirstFrame, 0, 0, Qt.AlignCenter)
		self.layout.addWidget(self.buttonPrevFrame, 0, 1, Qt.AlignCenter)
		self.layout.addWidget(self.buttonPlayPause, 0, 2, Qt.AlignRight)
		self.layout.addWidget(self.buttonNextFrame, 0, 3, Qt.AlignRight)
		self.layout.addWidget(self.buttonLastFrame, 0, 4, Qt.AlignLeft)
		self.layout.addWidget(self.currentFrameLineEdit, 0, 5, Qt.AlignLeft)
		self.layout.addWidget(self.labelOf, 0, 6, Qt.AlignLeft)
		self.layout.addWidget(self.lastFrameLineEdit, 0, 7, Qt.AlignLeft)

		self.setLayout(self.layout)
		
		self.__registerCallbacks()


	def __registerCallbacks(self):
		self.buttonFirstFrame.pressed.connect(self.buttonFirstFramePressed)
		self.buttonLastFrame.pressed.connect(self.buttonLastFramePressed)
		self.buttonPrevFrame.pressed.connect(self.buttonPrevFramePressed)
		self.buttonNextFrame.pressed.connect(self.buttonNextFramePressed)
		self.buttonPlayPause.pressed.connect(self.buttonPlayPausePressed)
		self.currentFrameLineEdit.editingFinished.connect(self.currentFrameLineEditChanged)

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

	def buttonPlayPausePressed(self):
		self.callback_togglePlay()

	def currentFrameLineEditChanged(self):
		self.callback_setFrameNum(int(self.currentFrameLineEdit.text()))
