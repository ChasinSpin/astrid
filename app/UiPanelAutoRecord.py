from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox
from settings import Settings
from datetime import datetime, timedelta
from UiDialogPanel import UiDialogPanel



class UiPanelAutoRecord(UiPanel):
	# Initializes and displays a Panel

	PANEL_WIDTH = 700
	TEXT_BOX_WIDTH = PANEL_WIDTH - 20
	TEXT_BOX_HEIGHT = 280

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.object		= args['object']
		self.camera		= args['camera']
		self.panel		= panel

		self.widgetInfo		= self.addTextBox('IMPORTANT PREREQUISITES FOR AUTO RECORDING:\n' \
			'\n' \
			'1. Telescope is already on target and tracking OR prepointed\n' \
			'2. Frame rate and gain are set to the correct values\n' \
			'3. Calculated start/end times are correct for the occultation\n' \
			'4. All status buttons (bottom right) are green consistently\n' \
			'5. Target is within the Field Of View of the Telescope/Camera\n' \
			'6. Focus remains stable thru recording\n' \
			'\n' \
			'If any of above are not true, press "Cancel" and address first.\n')


		start_time		= datetime.strptime(self.object['start_time'], '%Y-%m-%dT%H:%M:%S')
		end_time		= datetime.strptime(self.object['end_time'], '%Y-%m-%dT%H:%M:%S')

		self.trackingCapable	= Settings.getInstance().mount['tracking_capable']

		self.widgetStartTime	= self.addDateTimeEdit('Calculated Start Time(UTC)', editable=False)

		recordingSyncTime       = max( (self.camera.videoFrameDuration / 1000000.0) * self.camera.videoBufferCount, 12.0)
		start_time -= timedelta(seconds = recordingSyncTime)
		self.widgetStartTime.setDateTime(start_time)

		self.widgetEndTime	= self.addDateTimeEdit('Calculated End Time(UTC)', editable=False)
		self.widgetEndTime.setDateTime(end_time)

		self.widgetRecDuration	= self.addLineEdit('Recording Duration(s)', editable=False)
		self.updateRecordingDuration()

		self.widgetAutoRecord	= self.addButton('Start Auto Record', True)
		self.widgetCancel	= self.addButton('Cancel', True)

		self.setFixedWidth(UiPanelAutoRecord.PANEL_WIDTH)
		self.widgetInfo.setFixedSize(UiPanelAutoRecord.TEXT_BOX_WIDTH, UiPanelAutoRecord.TEXT_BOX_HEIGHT)
		#self.setColumnWidth(1, UiPanelAutoRecord.TEXT_BOX_WIDTH)
		

	def registerCallbacks(self):
		self.widgetAutoRecord.clicked.connect(self.buttonAutoRecordPressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)

	
	# CALLBACKS

	def buttonAutoRecordPressed(self):
		self.start_time	= self.widgetStartTime.dateTime().toPyDateTime()
		self.end_time	= self.widgetEndTime.dateTime().toPyDateTime()
		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()
	

	# OPERATIONS

	def updateRecordingDuration(self):
		start_time		= self.widgetStartTime.dateTime().toPyDateTime()
		end_time		= self.widgetEndTime.dateTime().toPyDateTime()
		recordingDuration	= (end_time - start_time).seconds
		self.widgetRecDuration.setText('%d' % recordingDuration)
