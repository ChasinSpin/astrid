from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox



"""
	Subclasses QMessageBox to add an autoClose(milliseconds).
	To use, use the exec template and set autoClose before the exec
"""

class UiAutoCloseMessageBox(QMessageBox):

	def __init__(self, *args, **kwargs):
		QMessageBox.__init__(self, *args, **kwargs)	
		self.autoClose = 0

	
	def showEvent(self, event):
		super().showEvent(event)
		if self.autoClose > 0:
			self.closeTimer = QTimer()
			self.closeTimer.timeout.connect(self.closeTimerEvent)
			self.closeTimer.start(self.autoClose)


	def closeTimerEvent(self):
		self.done(0)
