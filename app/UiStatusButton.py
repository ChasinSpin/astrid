from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QTimer



class UiStatusButton(QPushButton):

	STATUS_DISABLED	= 'Disabled'
	STATUS_UNKNOWN	= 'Unknown'
	STATUS_POOR	= 'Poor'
	STATUS_ADEQUATE	= 'Adequate'
	STATUS_GOOD	= 'Good'


	colorsForStatus = {STATUS_DISABLED: 'gray', STATUS_UNKNOWN: 'purple', STATUS_POOR: '#FF3333', STATUS_ADEQUATE: '#FFCC00', STATUS_GOOD: '#00FF00'}
	alternateColorsForStatus = {STATUS_DISABLED: 'gray', STATUS_UNKNOWN: '#7F007F', STATUS_POOR: '#7F0000', STATUS_ADEQUATE: '#7F4400', STATUS_GOOD: '#007F00'}


	def __init__(self, buttonText):
		super().__init__(buttonText)

		self.flashTimer = QTimer()
		self.flashTimer.timeout.connect(self.__flashTimerEvent)
		self.flashTimer.setInterval(1000)
		self.flashTimer.start()
		self.flashCounter = 0

		self.lastStatus = UiStatusButton.STATUS_DISABLED

		self.setStatus(UiStatusButton.STATUS_POOR)


	def setEnabled(self, enabled):
		super().setEnabled(enabled)
		if enabled:
			self.status = self.lastStatus
		else:
			self.status = UiStatusButton.STATUS_DISABLED
	

	def setStatus(self, status):
		if status == self.lastStatus:
			return

		self.status = status
		self.lastStatus = self.status
		color = UiStatusButton.colorsForStatus[status]
		self.setStyleSheet('border: 2px solid %s;color: %s;' % (color, color))

		self.flashTimer.stop()
		if self.status != UiStatusButton.STATUS_GOOD:
			self.flashCounter = 0
			self.flashTimer.start()


	def __flashTimerEvent(self):
		self.flashCounter += 1

		if (self.flashCounter % 2) == 0:
			color = UiStatusButton.colorsForStatus[self.status]
			self.setStyleSheet('border: 2px solid %s;color: %s;' % (color, color))
		else:
			color = UiStatusButton.alternateColorsForStatus[self.status]
			self.setStyleSheet('border: 2px solid %s;color: %s;' % (color, color))
