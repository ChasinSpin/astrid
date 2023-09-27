from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from UiQDialog import UiQDialog

class UiDialogPanel():

	def __init__(self, title, uiPanel, args = None, parent = None, modal = True):
		super().__init__()

		self.dialog = UiQDialog(parent = parent, topLeft = (260, 20))

		self.dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)

		if args is not None:
			self.dialog.panel = uiPanel(title, self, args)
		else:
			self.dialog.panel = uiPanel(title, self)
		
		self.dialog.panel.registerCallbacks()

		self.dialogLayout = QVBoxLayout()
		self.dialogLayout.addWidget(self.dialog.panel)
		self.dialog.setLayout(self.dialogLayout)

		if modal:
			self.dialog.exec()
		else:
			self.dialog.show()
			#self.dialog.raise()

	def cancelDialog(self):
		if self.dialog is not None:
			self.dialog.reject()

	def acceptDialog(self):
		if self.dialog is not None:
			self.dialog.accept()

	def done(self, value):
		if self.dialog is not None:
			self.dialog.done(value)


	def result(self):
		if self.dialog is not None:
			return self.dialog.result()
		else:
			return None
