#!/usr/bin/env python3

import os
import csv
import pickle
import kmeans1d
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QLabel



TEST_MODE		= False
PICKLE_FILE		= 'qualify_drive_DELETEME.pickle'

THROUGHPUT_30FPS	= 60.0
CHART_SIZE		= (800, 600)

DRIVE			= "/media/pi/ASTRID"



def runWriteTest():
	proc = subprocess.Popen( ['/home/pi/astrid/writetest/writetest', '2000000', '10', DRIVE], stdout=subprocess.PIPE)
	
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
	for entry in data:
		speed = float(entry['Speed(MB/s)'])
		allSpeeds.append(speed)

		if firstEntry:
			minSpeed = maxSpeed = speed
			firstEntry = False
		else:
			minSpeed = min(minSpeed, speed)
			maxSpeed = max(maxSpeed, speed)

	# Reference: https://github.com/dstein64/kmeans1d
	k = 2
	clusters, centroids = kmeans1d.cluster(allSpeeds, 2)
	print('Clusters:', clusters)

	return { 'minSpeed': minSpeed, 'maxSpeed': maxSpeed, 'centroids': centroids }


def chartWriteTest(writeTest, maxSpeed, centroids, title):
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

	# Setup centroid 0 & 1
	seriesCentroid0 = QLineSeries()
	seriesCentroid1 = QLineSeries()
	series30fps	= QLineSeries()
	for entry in writeTest:
		seriesCentroid0.append(float(entry['Total GB Transferred']), centroids[0])
		seriesCentroid1.append(float(entry['Total GB Transferred']), centroids[1])
		series30fps.append(float(entry['Total GB Transferred']), THROUGHPUT_30FPS)
	seriesCentroid0.setName('Centroid 0')
	seriesCentroid1.setName('Centroid 1')
	series30fps.setName('30fps Minimum')

	# Set seriesControid0 and seriesCentroid1 to be dotted
	pen = QPen()
	pen.setStyle(Qt.DashLine)
	pen.setColor(QColor(0xFF00FF))
	seriesCentroid0.setPen(pen)
	seriesCentroid1.setPen(pen)

	# Set series30fps to be dotted
	pen = QPen()
	pen.setStyle(Qt.DashLine)
	pen.setColor(QColor(0x00FF00))
	series30fps.setPen(pen)

	# Setup axis
	axisX = QValueAxis()
	#axisX.setRange(0, 30)
	axisX.setLabelFormat("%d")
	#axisX.setTickCount(int(max_mag-min_mag) + 1)
	axisX.setTickCount(5)
	axisX.setTitleText('Gigabytes Transferred (GB)')

	axisY = QValueAxis()
	axisY.setRange(0, maxSpeed)
	axisY.setLabelFormat("%d")
	axisY.setTickCount(5)
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
	for series in [series, seriesCentroid0, seriesCentroid1, series30fps]:
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
	result = runCommand(['/usr/bin/lsblk', '-o', 'KNAME,MOUNTPOINT,SERIAL'])
	result = result.split('\n')	

	# Find the line with the mount point in, this will be sda1 (not the USB drive) for example
	found = None
	for line in result:
		if DRIVE in line:
			found = line
			break

	# Now extract the sda1 and remove the number to get sda
	if found is not None:
		deviceName = found.split(' ')[0]
		deviceNameStripped = []
		for i in deviceName:
			if not i.isdigit():
				deviceNameStripped.append(i)
		deviceName = ''.join(deviceNameStripped)
		#print('DeviceName:', deviceName)

	# Now search the output for deviceName and extra the serial
	serial = None
	for line in result:
		if line.startswith(deviceName + ' '):
			serial = line[30:]
			break

	if serial is not None:
		print('Serial:', serial)

	result = runCommand(['/usr/bin/usb-devices'])
	result = result.split('\n')	

	found = False
	for line in result:
		if line.startswith('S:  Manufacturer='):
			manufacturer=line.replace('S:  Manufacturer=', '')
		if line.startswith('S:  Product='):
			product=line.replace('S:  Product=', '')
		if line.startswith('S:  SerialNumber='):
			serialNumber=line.replace('S:  SerialNumber=', '')
			if serialNumber == serial:
				found = True
				break

	if found:
		return (manufacturer, product, serialNumber)
	return None



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
chartview = chartWriteTest(writeTest, results['maxSpeed'], results['centroids'], title)
layout.addWidget(chartview)

window.setCentralWidget(mainWidget)

window.setWindowTitle('Qualify Drive')

window.show()

app.exec()
