from PyQt5.QtWidgets import QSplashScreen, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap



class UiSplashScreen():

	def __init__(self):
		super().__init__()

		pixmap = QPixmap('splash_images/1.png')
		self.splash = QSplashScreen(pixmap)

		self.splash.setFixedSize(600, 327)
		self.splash.show()

		# Center on teh screen 
		rect = self.splash.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		rect.moveCenter(centerPoint)
		self.splash.move(rect.topLeft())


	def setMessage(self, msg):
		self.splash.setStyleSheet("font: bold 24px;")
		self.splash.showMessage(msg, Qt.AlignVCenter | Qt.AlignHCenter, Qt.green)
		self.splash.repaint()


	def close(self):
		self.splash.close()
		self.splash = None
