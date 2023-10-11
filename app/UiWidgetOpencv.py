from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel



class UiWidgetOpencv(QWidget):

	def __init__(self, width, height):
		super().__init__()
		self.width		= width
		self.height		= height

		self.imageWidget	= QLabel()

		gray			= QPixmap(self.width, self.height)
		gray.fill(QColor(50,50,50))
	
		self.imageWidget.setPixmap(gray)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.imageWidget)
		self.setLayout(self.layout)


	def updateWithCVImage(self, image):
		image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale16)
		self.imageWidget.setPixmap(QPixmap.fromImage(image))
