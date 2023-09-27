from UiPanel import UiPanel
from PyQt5.QtCore import Qt, QTimer
from otestamper import OteStamper



class UiPanelAcquisition(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel):
		super().__init__(title)
		self.panel			= panel

		self.label1			= self.addLabel('Picamera2 Library:')
		self.widgetDroppedCamera	= self.addLineEdit('    Dropped Camera Frames', editable=False)
		self.widgetBadFrameDelta	= self.addLineEdit('    Bad Frame Delta', editable=False)
		self.spacer1			= self.addSpacer()

		self.label2			= self.addLabel('OTEStamper:')
		self.widgetDroppedOTEStamper	= self.addLineEdit('    Dropped OTEStamper Frames', editable=False)
		self.widgetCommsFailed		= self.addLineEdit('    OTEStamper Comms Failed', editable=False)
		self.widgetClockDrift		= self.addLineEdit('    Clock Drift', editable=False)
		self.widgetBadClockDrift	= self.addLineEdit('    Bad Clock Drifts', editable=False)
		self.widgetGetFrameInfoNoData	= self.addLineEdit('    OTEStamper No Data', editable=False)
		self.widgetGetFrameInfoNotReady	= self.addLineEdit('    OTEStamper Not Ready', editable=False)
		self.widgetSequence		= self.addLineEdit('    Frame Sequence Out Of Sync', editable=False)
		self.widgetEndDateTime		= self.addLineEdit('    Frame Timestamp Out Of Order', editable=False)
		self.widgetClockStatus		= self.addLineEdit('    Clock Status != 0x07 or 0x0B', editable=False)
		self.spacer2			= self.addSpacer()


		self.label3			= self.addLabel('RavfWriter:')
		self.widgetFinalFrameNotWritten	= self.addLineEdit('    Final Frame Not Written', editable=False)

		self.widgetReset		= self.addButton('Reset Counters')
		self.widgetCancel		= self.addButton('Cancel')

		self.setColumnWidth(1, 110)

		self.updateTimer = QTimer()
		self.updateTimer.timeout.connect(self.__updateTimer)
		self.updateTimer.setInterval(500)
		self.updateTimer.start()


	def registerCallbacks(self):
		self.widgetReset.clicked.connect(self.buttonResetPressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)


	# CALLBACKS	

	def buttonResetPressed(self):
		OteStamper.getInstance().resetStatistics()	


	def buttonCancelPressed(self):
		self.updateTimer.stop()
		self.updateTimer = None
		self.panel.cancelDialog()


	# OPERATIONS

	def __updateTimer(self):
		otestamper = OteStamper.getInstance()
		statistics = otestamper.statistics
		if otestamper.frameInfo is not None:
			self.widgetClockDrift.setText('%0.3fus' % OteStamper.getInstance().frameInfo['captureClockSystemDrift'])
		else:
			self.widgetClockDrift.setText('Record Video')
		self.widgetDroppedCamera.setText(str(statistics['dropped_camera']))
		self.widgetDroppedOTEStamper.setText(str(statistics['dropped_otestamper']))
		self.widgetCommsFailed.setText(str(statistics['otestamper_comms_failed']))
		self.widgetBadClockDrift.setText(str(statistics['badClockDrift']))
		self.widgetBadFrameDelta.setText(str(statistics['badFrameDelta']))
		self.widgetGetFrameInfoNoData.setText(str(statistics['getFrameInfoNoData']))
		self.widgetGetFrameInfoNotReady.setText(str(statistics['getFrameInfoNotReady']))
		self.widgetFinalFrameNotWritten.setText(str(statistics['finalFrameNotWritten']))
		self.widgetSequence.setText(str(statistics['sequence']))
		self.widgetEndDateTime.setText(str(statistics['endDateTime']))
		self.widgetClockStatus.setText(str(statistics['clockStatus']))
