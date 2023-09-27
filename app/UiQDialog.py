from PyQt5.QtWidgets import QDialog, QDesktopWidget

class UiQDialog(QDialog):

	def __init__(self, parent = None, topLeft = None):
		super().__init__(parent = parent)
		self.topLeft = topLeft


	def showEvent(self, event):
		super().showEvent(event)
		self.centerInParent()


	def centerInParent(self):
		if self.parent() is None:
			rect = self.frameGeometry()
			centerPoint = QDesktopWidget().availableGeometry().center()		
			rect.moveCenter(centerPoint)
			self.move(rect.topLeft())
		else:
			posParent = self.parent().geometry().topLeft()
			self.move(posParent.x() + self.topLeft[0], posParent.y() + self.topLeft[1])
