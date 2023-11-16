import os
import subprocess
from UiPanel import UiPanel
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from settings import Settings


# Download Occelmnt Predictions on a seperate thread

class CatalogExtractThread(QThread):
        catalogExtractSuccess     = pyqtSignal()

        def __init__(self, filename):
                super(QThread, self).__init__()

                self.filename = filename


        def run(self):
                cmd = ['/usr/bin/tar', '--directory', Settings.getInstance().astrid_drive, '-xvf', self.filename]
                print(cmd)
                subprocess.run(args=cmd)

                os.remove(self.filename)

                self.catalogExtractSuccess.emit()



class UiPanelDisplay2(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, camera):
		super().__init__('Display 2')

		self.camera = camera
		self.widgetExpAnalysis	= self.addButton('Exposure Analysis')


	def registerCallbacks(self):
		self.widgetExpAnalysis.clicked.connect(self.buttonExpAnalysis)
		


	# CALLBACKS

	def buttonExpAnalysis(self):
		self.camera.annotationStars = None
		self.camera.updateDisplayOptions()

		unextracted_catalog = Settings.getInstance().astrid_drive + '/daveherald_star_catalogs_v1.txz'
		if os.path.exists(unextracted_catalog):
			self.thread = CatalogExtractThread(unextracted_catalog)
			self.thread.catalogExtractSuccess.connect(self.__catalogExtractSuccess)
			#self.thread.finished.connect(self.thread.deleteLater)
			self.thread.start()

			self.catalogExtractMsgBox = QMessageBox()
			self.catalogExtractMsgBox.setIcon(QMessageBox.Information)
			self.catalogExtractMsgBox.setText('Please wait, extracting catalog...')
			self.catalogExtractMsgBox.setStandardButtons(QMessageBox.NoButton)

			self.catalogExtractMsgBox.exec()

		gaia_index = Settings.getInstance().astrid_drive + '/catalogs/daveherald/Gaia16_EDR3.inx'

		if not os.path.exists(gaia_index):
			QMessageBox.warning(self, ' ', 'Star Catalog Requires Downloading.\n\nDownload:\n    https://astrid-downloads.s3.amazonaws.com/downloads/daveherald_star_catalogs_v1.txz\n\n and place at top level of USB Thumb Drive', QMessageBox.Ok)
		else:
			self.camera.ui.panelTask.buttonPlateSolvePressed(True, expAnalysis = True)
       

	# OPERATIONS

	def __catalogExtractSuccess(self):
		self.catalogExtractMsgBox.done(0)
		self.catalogExtractMsgBox = None
		self.thread.wait()
		self.thread = None
