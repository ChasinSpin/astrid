from PyQt5 import QtWidgets
from PyQt5.QtChart import QChart, QChartView
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout



class UiWidgetChart(QWidget):

	def __init__(self, width, height):
		super().__init__()
		self.width		= width
		self.height		= height

		self.chart = QChart()
		self.chartview = QChartView(self.chart)
		self.chartview.setRenderHint(QPainter.Antialiasing)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.chartview)
		self.setLayout(self.layout)

		self.chartview.setFixedSize(self.width, self.height)
