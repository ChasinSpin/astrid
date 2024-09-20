import math
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from settings import Settings
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
		self.labelRa	= None
		self.labelDec	= None
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


	def __degToDMS(self, degrees):
		d = abs(degrees)
		deg = math.floor(d)
		d = d - deg
		d = d * 60
		min = math.floor(d)
		d = d - min
		d = d * 60
		sec = d
	
		if degrees < 0:
			deg = -deg

		return (deg, min, sec)		
		

	def __raDecToTxt(self, ra, dec):
		self.radec_format = Settings.getInstance().camera['radec_format']

		if self.radec_format == 'hour':
			ra = (ra / 360.0) * 24.0
			raStr = '%0.5f' % ra
			decStr = '%0.5f' % dec
		elif self.radec_format == 'hmsdms':
			ra = (ra / 360.0) * 24.0

			raComponents = self.__degToDMS(ra)
			decComponents = self.__degToDMS(dec)

			raStr = '%0.0fh%0.0fm%0.4fs' % (raComponents[0], raComponents[1], raComponents[2])
			decStr = '%0.0fd%0.0fm%0.4fs' % (decComponents[0], decComponents[1], decComponents[2])
		elif self.radec_format == 'deg':
			raStr = '%0.5f' % ra
			decStr = '%0.5f' % dec

		if ra > 0:
			raStr = '+' + raStr
		if dec > 0:
			decStr = '+' + decStr

		return (raStr, decStr)


	# arrows is the number of arrows to display, 2 or 1

	def update(self, ra, dec, altitude, azimuth, arrows, isPrepoint):
		if self.layout is None:
			createWidgets = True
		else:
			createWidgets = False

		if createWidgets:
			self.layout = QGridLayout()

		if arrows == '2 Arrows':
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

		elif arrows == '1 Arrow':
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

		elif arrows == 'Ra/Dec':
			if createWidgets:
				self.labelRaTitle = QLabel()
				self.labelDecTitle = QLabel()
				self.labelRa = QLabel()
				self.labelDec = QLabel()
				if isPrepoint:
					self.labelPrepointWarning = QLabel()
					self.labelSpacer = QLabel()

			self.labelRaTitle.setText('Delta RA')
			self.labelDecTitle.setText('Delta DEC')
			raDecStr = self.__raDecToTxt(ra, dec)
			self.labelRa.setText(raDecStr[0])
			self.labelDec.setText(raDecStr[1])
			if isPrepoint:
				self.labelPrepointWarning.setText('Warning: RA/DEC deltas change\nduring prepointing as earth rotates')
				self.labelSpacer.setText(' ')

			rotation = math.degrees(math.atan2(azimuth, altitude))
			arrowNew = self.__arrowLabel(rotation)

			if createWidgets:
				self.layout.addWidget(arrowNew, 0, 0, 2, 0, Qt.AlignCenter)
			else:
				self.arrow.hide()
				self.layout.replaceWidget(self.arrow, arrowNew)
				self.arrow.deleteLater()

			self.arrow = arrowNew

			if createWidgets:
				self.layout.addWidget(self.labelRaTitle, 2, 0, Qt.AlignLeft)
				self.layout.addWidget(self.labelRa, 2, 1, Qt.AlignLeft)

				self.layout.addWidget(self.labelDecTitle, 3, 0, Qt.AlignLeft)
				self.layout.addWidget(self.labelDec, 3, 1, Qt.AlignLeft)

				if isPrepoint:
					self.layout.addWidget(self.labelSpacer, 4, 0, Qt.AlignLeft)
					self.layout.addWidget(self.labelPrepointWarning, 5, 0, 2, 0, Qt.AlignLeft)

		if createWidgets:
			self.setLayout(self.layout)
			self.setFixedWidth(UiWidgetDirection.WIDTH)
