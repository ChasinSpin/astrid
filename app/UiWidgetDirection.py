import math
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel



class UiWidgetDirection(QWidget):
	WIDTH = 250

	def __init__(self):
		super().__init__()
		self.layout	= None
		self.labelVert	= None
		self.labelHoriz	= None
		self.arrowVert	= None
		self.arrowHoriz	= None
		self.label	= None
		self.arrow	= None


	def __arrowLabel(self, rotation) -> QLabel:
		pixmap = QPixmap('arrow.png')
		transform = QTransform().rotate(rotation)
		pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

		label = QLabel()
		label.setPixmap(pixmap)

		return label


	def __degToTxt(self, deg):
		if deg >= 1.0:
			return '%0.3f deg' % (deg)
		else:
			return '%0.3f arcmin' % (deg * 60.0)


	# arrows is the number of arrows to display, 2 or 1

	def update(self, altitude, azimuth, arrows):
		if self.layout is None:
			createWidgets = True
		else:
			createWidgets = False

		if createWidgets:
			self.layout = QGridLayout()

		if arrows == 2:
			if createWidgets:
				self.labelVert = QLabel()
				self.labelHoriz = QLabel()

			self.labelVert.setText(self.__degToTxt(abs(altitude)))
			self.labelHoriz.setText(self.__degToTxt(abs(azimuth)))

			arrowVertNew = self.__arrowLabel(180 if altitude < 0 else 0)
			arrowHorizNew = self.__arrowLabel(270 if azimuth < 0 else 90)

			if createWidgets:
				self.layout.addWidget(arrowHorizNew, 0, 0, Qt.AlignCenter)
				self.layout.addWidget(arrowVertNew, 1, 0, Qt.AlignCenter)
			else:
				self.arrowHoriz.hide()
				self.arrowVert.hide()
				self.layout.replaceWidget(self.arrowHoriz, arrowHorizNew)
				self.layout.replaceWidget(self.arrowVert, arrowVertNew)
				self.arrowHoriz.deleteLater()
				self.arrowVert.deleteLater()

			self.arrowHoriz = arrowHorizNew
			self.arrowVert = arrowVertNew
				

			if createWidgets:
				self.layout.addWidget(self.labelHoriz, 0, 1, Qt.AlignCenter)
				self.layout.addWidget(self.labelVert, 1, 1, Qt.AlignCenter)

		elif arrows == 1:
			if createWidgets:
				self.label = QLabel()

			self.label.setText(self.__degToTxt(math.sqrt(altitude * altitude + azimuth * azimuth)))

			rotation = math.degrees(math.atan2(azimuth, altitude))
			arrowNew = self.__arrowLabel(rotation)

			if createWidgets:
				self.layout.addWidget(arrowNew, 0, 0, Qt.AlignCenter)
			else:
				self.arrow.hide()
				self.layout.replaceWidget(self.arrow, arrowNew)
				self.arrow.deleteLater()

			self.arrow = arrowNew

			if createWidgets:
				self.layout.addWidget(self.label, 1, 0, Qt.AlignCenter)
	
		if createWidgets:
			self.setLayout(self.layout)
			self.setFixedWidth(UiWidgetDirection.WIDTH)
