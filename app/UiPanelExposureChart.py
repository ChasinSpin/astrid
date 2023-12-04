import os
import math
import numpy as np
from astropy.io import fits
from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPen, QLinearGradient, QGradient, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QAreaSeries
from PyQt5.QtCore import Qt, QPointF
from settings import Settings
from datetime import datetime, timedelta
from UiDialogPanel import UiDialogPanel
from astutils import AstUtils



class UiPanelExposureChart(UiPanel):
	# Initializes and displays a Panel

	PANEL_WIDTH = 800
	PANEL_HEIGHT = 800


	def __init__(self, title, panel, args):
		super().__init__(title)

		self.camera		= args['camera']
		self.stars		= args['stars']
		self.bkg_mean		= args['bkg_mean']
		self.bkg_median		= args['bkg_median']
		self.bkg_stddev		= args['bkg_stddev']
		self.fits_fname		= args['fits_fname']

		self.panel		= panel

		self.widgetChart	= self.addChart(700,600)
		self.chart		= self.widgetChart.chart
		self.makeChart()

		self.widgetSave		= self.addButton('Save Chart', True)
		self.widgetOK		= self.addButton('OK', True)

		self.setFixedSize(self.PANEL_WIDTH, self.PANEL_HEIGHT)
		#self.widgetInfo.setFixedSize(UiPanelAutoRecord.TEXT_BOX_WIDTH, UiPanelAutoRecord.TEXT_BOX_HEIGHT)
		#self.setColumnWidth(1, UiPanelAutoRecord.TEXT_BOX_WIDTH)
		

	def registerCallbacks(self):
		self.widgetSave.clicked.connect(self.buttonSavePressed)
		self.widgetOK.clicked.connect(self.buttonOKPressed)

	
	# CALLBACKS

	def buttonSavePressed(self):
		expcharts_folder = Settings.getInstance().astrid_drive + '/expcharts'
		if not os.path.isdir(expcharts_folder):
			os.mkdir(expcharts_folder)
		expchart_fname = expcharts_folder + '/ExposureChart_%s.png' % datetime.utcnow().strftime("%Y%m%d_%H%M%S")
		self.widgetChart.grab().save(expchart_fname)
		self.panel.acceptDialog()


	def buttonOKPressed(self):
		self.panel.acceptDialog()
	

	# OPERATIONS

	def makeChart(self):
		# Set Theme
		#self.chart.setTheme(QChart.ChartThemeBlueCerulean)
		#self.chart.setTheme(QChart.ChartThemeLight)
		self.chart.setTheme(QChart.ChartThemeDark)

		# Setup mag/exposure series
		brightness_x = []
		brightness_y = []
		seriesExposure = QLineSeries(self)
		min_mag = 1000
		max_mag = -1000
		for star in self.stars:
			mag = star.mag_g

			# If we're not saturated and we're more than 3 stddev above background,
			# calculate the brightneess and add to the list
			if star.peakSensor < 100.0 and star.peakSensor > (self.bkg_mean + self.bkg_stddev * 3):
				brightness_x.append(math.pow(10.0, -mag/2.51188643150958))
				brightness_y.append(star.peakSensor)

			seriesExposure.append(mag, star.peakSensor)
			min_mag = min(mag, min_mag)
			max_mag = max(mag, max_mag)
		min_mag = math.floor(min_mag)
		max_mag = math.ceil(max_mag)
		seriesExposure.setName('Star Peak')

		# Linfit through bightnesses
		brightnesses_coeffs = np.linalg.lstsq(np.vstack([brightness_x, np.ones(len(brightness_x))]).T, brightness_y, rcond=None)[0]

		# Generate the predicted lin fit line
		seriesPredicted = QLineSeries(self)
		for predictMag in np.arange(min_mag, max_mag, 0.01):
			predictedSensorSat = brightnesses_coeffs[0] * math.pow(10.0, -predictMag/2.51188643150958) + brightnesses_coeffs[1]           
			if predictedSensorSat < 0 or predictedSensorSat > 100.0:
				continue
			seriesPredicted.append(predictMag, predictedSensorSat)
		seriesPredicted.setName('Predicted Fit')

		# Set the prediction line to be dotted
		pen = QPen()
		pen.setStyle(Qt.DashLine)
		pen.setColor(QColor(0xFF00FF))
		seriesPredicted.setPen(pen)

		# Setup background upper limit (mean + 2 stddev)
		stddev2 = self.bkg_stddev * 2
		seriesBkgUpper = QLineSeries(self)
		seriesBkgUpper.append(min_mag, self.bkg_mean + stddev2)
		seriesBkgUpper.append(max_mag, self.bkg_mean + stddev2)

		# Setup background lower limit (mean - 2 stddev)
		seriesBkgLower = QLineSeries(self)
		seriesBkgLower.append(min_mag, self.bkg_mean - stddev2)
		seriesBkgLower.append(max_mag, self.bkg_mean - stddev2)

		# Setup series
		seriesSuggestedLimit = 33.0
		seriesSuggested = QLineSeries(self)
		seriesSuggested.append(min_mag, seriesSuggestedLimit)
		seriesSuggested.append(max_mag, seriesSuggestedLimit)
		seriesSuggested.setName('Suggested Max')

		# Setup Area between background lower and background upper
		seriesBkg = QAreaSeries(seriesBkgLower, seriesBkgUpper)
		seriesBkg.setName('Mean Background ± 2σ')
		penBkg = QPen(0x059605)
		penBkg.setWidth(3)
		seriesBkg.setPen(penBkg)

		# Create X and Y axis
		axisX = QValueAxis()
		axisX.setRange(min_mag, max_mag)
		axisX.setLabelFormat("%d")
		axisX.setTickCount(int(max_mag-min_mag) + 1)
		axisX.setTitleText('Magnitude')

		axisY = QValueAxis()
		axisY.setRange(0, 100)
		axisY.setLabelFormat("%d")
		axisY.setTickCount(5)
		axisY.setTitleText('% Sensor Saturation')

		# Add Axis
		self.chart.addAxis(axisX, Qt.AlignBottom)
		self.chart.addAxis(axisY, Qt.AlignLeft)

		# Setup chart options
		self.chart.setAnimationOptions(QChart.SeriesAnimations)
		self.chart.legend().setVisible(True)
		self.chart.legend().setAlignment(Qt.AlignBottom)

		# Read fits information we need for the title
		hdul		= fits.open(self.fits_fname)
		gain		= int(round(hdul[0].header['GAIN']))
		focalLen	= int(round(hdul[0].header['FOCALLEN']))
		expTime		= hdul[0].header['EXPTIME']
		telescope	= hdul[0].header['TELESCOP'] 
		if telescope == 'my telescope':
			configName = ''
		else:
			configName = telescope + '<br />'
		hdul.close()

		self.chart.setTitle('<h3 style="text-align:center">%sF/L:%dmm Gain:%d Fps:%0.2f (%0.2fs)<br /></h3>' % (configName, focalLen, gain, (1.0/expTime), expTime))


		# Reduce size of chart frame
		self.chart.layout().setContentsMargins(1, 1, 1, 1)
		self.chart.setBackgroundRoundness(1)

		# Attach the series to the chart and the axis to the series
		for series in [seriesExposure, seriesBkg, seriesSuggested, seriesPredicted]:
			self.chart.addSeries(series)
			series.attachAxis(axisX)
			series.attachAxis(axisY)
