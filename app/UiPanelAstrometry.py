from UiPanel import UiPanel
from PyQt5.QtWidgets import QApplication


class UiPanelAstrometry(UiPanel):
	# Initializes and displays a Panel

	STATUSPROGRESS_WIDTH = 400

	def __init__(self, title, panel, astrometryDownload):
		super().__init__('Astrometry Download')
		self.panel = panel

		self.astrometryDownload = astrometryDownload

		self.widgetMessage	= self.addTextBox('Astrometry index files are needed for the focal length of this configuration.\n\nChoose "Download" to download these now.\n\n1. Failure to download these files will result in Plate Solving not working.\n2. Internet connection required for download.', 180)
		self.widgetMessage.setFixedWidth(600)

		self.widgetStatus	= self.addLineEdit('Downloading...', editable=False)
		self.widgetStatus.setFixedWidth(UiPanelAstrometry.STATUSPROGRESS_WIDTH)
		self.hideWidget(self.widgetStatus)

		self.widgetProgress	= self.addProgressBar('Percent Complete')
		self.widgetProgress.setFixedWidth(UiPanelAstrometry.STATUSPROGRESS_WIDTH)
		self.hideWidget(self.widgetProgress)

		self.widgetDownload	= self.addButton('Download')
		self.widgetCancel	= self.addButton('Ignore / Proceed Anyway')

		self.pos = None


	def registerCallbacks(self):
		self.widgetDownload.pressed.connect(self.buttonDownloadPressed)
		self.widgetCancel.pressed.connect(self.buttonCancelPressed)


	def buttonDownloadPressed(self):
		self.hideWidget(self.widgetMessage)
		self.widgetDownload.setEnabled(False)
		self.widgetCancel.setEnabled(False)
		self.showWidget(self.widgetProgress)
		self.showWidget(self.widgetStatus)
		self.pos = self.panel.dialog.pos()
		self.adjustSize()
		self.panel.dialog.adjustSize()
		self.panel.dialog.move(self.pos)
		self.astrometryDownload.download(self.updateDownloadStatus)
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()


	def updateDownloadStatus(self, percent, status):
		self.panel.dialog.move(self.pos)
		self.widgetProgress.setValue(percent)
		self.widgetStatus.setText(status)

		app = QApplication.instance()
		app.processEvents()
