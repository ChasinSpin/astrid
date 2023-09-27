from PyQt5.QtWidgets import QLabel
from UiStatusButton import UiStatusButton



class UiStatusLabel(QLabel):

	def __init__(self, labelText):
		super().__init__(labelText)
		self.setStatus(UiStatusButton.STATUS_POOR)


	def setStatus(self, status):
		self.status = status
		color = UiStatusButton.colorsForStatus[status]
		self.setStyleSheet('color: %s;' % color)
