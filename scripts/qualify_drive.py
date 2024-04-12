#!/usr/bin/env python3

import os
import csv
import pickle
import statistics
import kmeans1d
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel



TEST_MODE		= True
#PICKLE_FILE		= 'SANDISK_BAD.pickle'
#PICKLE_FILE		= 'SANDISK_GOOD.pickle'
#PICKLE_FILE		= 'CORSAIR.pickle'
PICKLE_FILE		= 'TOPESEL.pickle'
#PICKLE_FILE		= 'qualify_drive_DELETEME.pickle'

THROUGHPUT_30FPS	= 60.0
CHART_SIZE		= (800, 600)
PSLC_CLUSTER_CUTOFF	= 0.05		# This is the change in cluster identification. < 0.05 indicates we have 2 clusters, >= 0.05 indicates we have 1
TEST_SIZE_GB		= 10

DRIVE			= "/media/pi/ASTRID"



def runWriteTest():
	proc = subprocess.Popen( ['/home/pi/astrid/writetest/writetest', '2000000', '%d' % TEST_SIZE_GB, DRIVE], stdout=subprocess.PIPE)
	
	recording = False
	terminated = False
	csvContents = []
	while True:
		line = proc.stdout.readline().rstrip()

		return_code = proc.poll()
		if return_code is not None:
			terminated = True

		#print('Line:%s terminated:%s' % (line, terminated))
		if not line and terminated:
			break
		elif line:
			str = line.decode('ascii')

			if   str == '--- START OF DATA ---':
				recording = True
			elif str == '--- END OF DATA ---':
				recording = False
			elif recording:
				csvContents.append(str)

			print(str)

	if return_code == 0:
		csvReader = csv.DictReader(csvContents, delimiter=',')
		arr = []
		for d in csvReader:
			arr.append(d)
		return arr
	return None


def analyzeWriteTest(data):
	firstEntry = True
	minSpeed = None
	maxSpeed = None
	allSpeeds = []
	allCounts = []
	
	for entry in data:
		count = int(entry['Count'])
		speed = float(entry['Speed(MB/s)'])
		allCounts.append(count)
		allSpeeds.append(speed)

		if firstEntry:
			minSpeed = maxSpeed = speed
			firstEntry = False
		else:
			minSpeed = min(minSpeed, speed)
			maxSpeed = max(maxSpeed, speed)

	# Reference: https://github.com/dstein64/kmeans1d
	k = 2
	clusters, centroids = kmeans1d.cluster(allSpeeds, k)
	print('Clusters:', clusters)

	# Count how frequently the cluster membership switches
	clusterChanges = 0
	for i in range(1, len(clusters)):
		if clusters[i] != clusters[i-1]:
			clusterChanges += 1
	clusterChanges = clusterChanges / len(clusters)

	# Calculate the lower limits of each cluster
	lowerLimits = []
	pSLC = None
	if clusterChanges < PSLC_CLUSTER_CUTOFF:
		lowerLimits.append(centroids[0])
		lowerLimits.append(centroids[1])


		# Figure out the size of the pSLC
		pSLCCount = 0

		while pSLCCount < len(clusters):
			if clusters[pSLCCount] == 0:
				pSLC = data[pSLCCount-1]['Total GB Transferred']
				break
			pSLCCount += 1
	else:
		lowerLimits.append(statistics.median(allSpeeds))
	
	# Figure out the standard deviation of the values in the cluster
	for ll in range(len(lowerLimits)):
		values = []
		for i in range(len(allSpeeds)):
			if clusters[i] == ll:
				values.append(allSpeeds[i])
		stddev = statistics.stdev(values)
		lowerLimits[ll] -= stddev

	# Flip lower limits so the highest is first
	if len(lowerLimits) >= 2 and lowerLimits[0] < lowerLimits[1]:
		tmp = lowerLimits[1]
		lowerLimits[1] = lowerLimits[0]
		lowerLimits[0] = tmp

	return { 'minSpeed': minSpeed, 'maxSpeed': maxSpeed, 'lowerLimits': lowerLimits, 'clusterChanges': clusterChanges, 'pSLC': pSLC }


def chartWriteTest(writeTest, maxSpeed, lowerLimits, title):
	chart = QChart()
	chartview = QChartView(chart)
	chartview.setRenderHint(QPainter.Antialiasing)
	chartview.setFixedSize(CHART_SIZE[0], CHART_SIZE[1])

	# Style chart
	chart.setTheme(QChart.ChartThemeDark)

	# Setup series data
	series = QLineSeries()
	for entry in writeTest:
		series.append(float(entry['Total GB Transferred']), float(entry['Speed(MB/s)']))
	series.setName('Throughput')

	pen = QPen()
	pen.setColor(QColor(0x00FF00))
	pen.setWidth(2)
	series.setPen(pen)

	# Setup centroid 0 & 1
	seriesCentroids = []
	for limit in lowerLimits:
		seriesCentroids.append(QLineSeries())
	series30fps	= QLineSeries()
	for entry in writeTest:
		for i in range(len(lowerLimits)):
			seriesCentroids[i].append(float(entry['Total GB Transferred']), lowerLimits[i])
		series30fps.append(float(entry['Total GB Transferred']), THROUGHPUT_30FPS)
	if len(lowerLimits) == 2:
		seriesCentroids[0].setName('Cached Base Rate')
		seriesCentroids[1].setName('Non-Cached Base Rate')
	elif len(lowerLimits) == 1:
		seriesCentroids[0].setName('Base Rate')
	series30fps.setName('30fps Minimum')

	# Set seriesControids to be dotted
	if len(lowerLimits) == 2:
		pen = QPen()
		pen.setStyle(Qt.DashLine)
		pen.setColor(QColor(0xFF00FF))
		pen.setWidth(2)
		seriesCentroids[1].setPen(pen)

	pen = QPen()
	pen.setStyle(Qt.DashLine)
	pen.setColor(QColor(0x00FFFF))
	pen.setWidth(2)
	seriesCentroids[0].setPen(pen)

	# Set series30fps to be dotted
	pen = QPen()
	pen.setStyle(Qt.DashLine)
	pen.setColor(QColor(0xFF0000))
	pen.setWidth(2)
	series30fps.setPen(pen)

	# Setup axis
	axisX = QValueAxis()
	axisX.setTickType(QValueAxis.TicksDynamic)
	axisX.setRange(0, TEST_SIZE_GB)
	axisX.setLabelFormat("%d")
	axisX.setTickAnchor(0)
	axisX.setTickInterval(1.0)
	axisX.setTitleText('Gigabytes Transferred (GB)')

	axisY = QValueAxis()
	axisY.setTickType(QValueAxis.TicksDynamic)
	topRange = int(( maxSpeed + 25) / 25) * 25
	axisY.setRange(0, topRange)
	axisY.setLabelFormat("%d")
	axisX.setTickAnchor(0)
	axisY.setTickInterval(25.0)
	axisY.setTitleText('Transfer Rate (MB/s)')

	# Add Axis
	chart.addAxis(axisX, Qt.AlignBottom)
	chart.addAxis(axisY, Qt.AlignLeft)

	# Setup chart options
	chart.setAnimationOptions(QChart.SeriesAnimations)
	chart.legend().setVisible(True)
	chart.legend().setAlignment(Qt.AlignBottom)	

	chart.setTitle('<h3 style="text-align:center">%s</h3>' % title)

	# Reduce the size of the chart frame
	chart.layout().setContentsMargins(1, 1, 1, 1)
	chart.setBackgroundRoundness(1)

	# Add series to charts
	
	for series in [series, series30fps]:
		chart.addSeries(series)
		series.attachAxis(axisX)
		series.attachAxis(axisY)

	for series in seriesCentroids:
		chart.addSeries(series)
		series.attachAxis(axisX)
		series.attachAxis(axisY)

	return chartview


def runCommand(cmd, line_starts_with = None):
	"""
		Runs a command, cmd is an array consisting of the command and parameters
		If line_starts_with is set to a str, the first line with starting with that string is returned,
		otherwise returns stdout from the command
	"""
	result = subprocess.run(cmd, capture_output = True, text = True)
	if line_starts_with is not None:
		lines = result.stdout.split('\n')
		for line in lines:
			if line.startswith(line_starts_with):
				return line
	return result.stdout



def getUsbDetails():
	result = runCommand(['/home/pi/astrid/scripts/astrid-drive-info.sh'])
	result = result.split('\n')	

	for line in result:
		if line.startswith('USB_MANUFACTURER='):
			manufacturer=line.replace('USB_MANUFACTURER=', '')
		if line.startswith('USB_PRODUCT='):
			product=line.replace('USB_PRODUCT=', '')
		if line.startswith('USB_SERIAL='):
			serialNumber=line.replace('USB_SERIAL=', '')

	return (manufacturer, product, serialNumber)



#
# MAIN
#

if TEST_MODE:
	if os.path.exists(PICKLE_FILE):
		fp = open(PICKLE_FILE, 'rb')
		writeTest = pickle.load(fp)
		fp.close()
	else:
		writeTest = runWriteTest()
		fp = open(PICKLE_FILE, 'wb')
		pickle.dump(writeTest, fp)
		fp.close()
else:
	writeTest = runWriteTest()

results = analyzeWriteTest(writeTest)
print(results)

app = QApplication([])

window = QMainWindow()

mainWidget = QWidget()
layout = QVBoxLayout(mainWidget)
label = QLabel('Performance Test')
layout.addWidget(label)

(manufacturer, product, serialNumber) = getUsbDetails()
title = '%s : %s : %s' % (manufacturer, product, serialNumber)
chartview = chartWriteTest(writeTest, results['maxSpeed'], results['lowerLimits'], title)
layout.addWidget(chartview)

window.setCentralWidget(mainWidget)

window.setWindowTitle('Qualify Drive')

window.show()

app.exec()
