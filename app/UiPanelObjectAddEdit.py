from UiPanel import UiPanel
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from settings import Settings
from astcoord import AstCoord
import xmltodict
from datetime import datetime, timedelta



class UiPanelObjectAddEdit(UiPanel):
	# Initializes and displays a Panel

	def __init__(self, title, panel, args):
		super().__init__(title)

		self.radec_format = Settings.getInstance().camera['radec_format']

		self.database		= args['database']
		self.camera		= args['camera']
		self.editValues		= args['editValues']
		self.panel		= panel

		self.widgetName		= self.addLineEdit('Object Name')

		if self.database == 'Occultations' and self.editValues is None:
			self.widgetOccelmnt		= self.addTextEdit('Occelmnt', 'Copy and paste occelmnt data for the event here')
		else:
			self.widgetOccelmnt		= None

		if self.radec_format == 'hour':
			self.widgetRA		= self.addLineEditDouble('RA', 0.0, 23.9999999999, 10, editable=True)
			self.widgetDEC		= self.addLineEditDouble('DEC', -90.0, 90.0, 10, editable=True)
		elif self.radec_format == 'hmsdms':
			self.widgetRA  = self.addCoordHMS('RA (HMS)')
			self.widgetDEC = self.addCoordDMS('DEC (DMS)')
			self.widgetRA.setValue(0, 0, 0.000)
			self.widgetDEC.setValue(0, 0, 0.000)
		elif self.radec_format == 'deg':
			self.widgetRA		= self.addLineEditDouble('RA', 0.0, 359.9999999999, 10, editable=True)
			self.widgetDEC		= self.addLineEditDouble('DEC', -90.0, 90.0, 10, editable=True)

		if self.database == 'Occultations':
			self.widgetEventTime		= self.addDateTimeEdit('Event Center Time(UTC)')
			self.widgetEventDuration	= self.addLineEditDouble('Max Duration(s)', 0.001, 86400.0, 3, editable=True)
			self.widgetEventUncertainty	= self.addLineEditDouble('Error in time(s)', 0.001, 86400.0, 3, editable=True)

			if self.editValues is None:
				self.widgetExtraStart		= self.addLineEditInt('Add Secs@Start', 1, 86400, editable=True)
				self.widgetExtraEnd		= self.addLineEditInt('Add Secs@End', 1, 86400, editable=True)
				self.widgetSpacer		= self.addSpacer()
			else:
				self.widgetExtraStart		= None
				self.widgetExtraEnd		= None
				self.widgetSpacer		= None

			self.widgetStartTime		= self.addDateTimeEdit('Calculated Start Time(UTC)', editable=False if self.editValues is None else True)
			self.widgetEndTime		= self.addDateTimeEdit('Calculated End Time(UTC)', editable=False if self.editValues is None else True)

			if self.editValues is None:
				self.widgetRecDuration		= self.addLineEdit('Recording Duration(s)', editable=False)
			else:
				self.widgetRecDuration		= None
			
			self.widgetEventDuration.setText('0.0')
			self.widgetEventUncertainty.setText('0.0')

			if self.editValues is None:
				self.widgetExtraStart.setText('30')
				self.widgetExtraEnd.setText('30')
		else:
			self.widgetEventTime		= None
			self.widgetEventDuration	= None
			self.widgetEventUncertainty	= None
			self.widgetOccelmnt		= None
			self.widgetExtraStart		= None
			self.widgetExtraEnd		= None
			self.widgetStartTime		= None
			self.widgetEndTime		= None
			self.widgetRecDurationx		= None

		if self.editValues is not None:
			self.widgetName.setText(self.editValues['name'])
			
			if self.radec_format == 'hour':
				coord = AstCoord.from360Deg(self.editValues['ra'], self.editValues['dec'], 'icrs')
				radec = coord.raDec24Deg('icrs')
				self.widgetRA.setText('%0.10f' % radec[0])
				self.widgetDEC.setText('%0.10f' % radec[1])
			elif self.radec_format == 'hmsdms':
				coord = AstCoord.from360Deg(self.editValues['ra'], self.editValues['dec'], 'icrs')
				radec = coord.raDecHMS('icrs')
				self.widgetRA.setValue(radec[0][0], radec[0][1], radec[0][2])
				self.widgetDEC.setValue(radec[1][0], radec[1][1], radec[1][2])
			elif self.radec_format == 'deg':
				self.widgetRA.setText('%0.10f' % self.editValues['ra'])
				self.widgetDEC.setText('%0.10f' % self.editValues['dec'])

			if self.database == 'Occultations':
				self.widgetEventTime.setDateTime(datetime.strptime(self.editValues['event_time'], '%Y-%m-%dT%H:%M:%S'))
				self.widgetEventDuration.setText('%0.1f' % self.editValues['event_duration'])
				self.widgetEventUncertainty.setText('%0.1f' % self.editValues['event_uncertainty'])
				self.widgetStartTime.setDateTime(datetime.strptime(self.editValues['start_time'], '%Y-%m-%dT%H:%M:%S'))
				self.widgetEndTime.setDateTime(datetime.strptime(self.editValues['end_time'], '%Y-%m-%dT%H:%M:%S'))

		self.widgetAdd		= self.addButton('Add' if self.editValues is None else 'Update', True)

		self.widgetCancel	= self.addButton('Cancel', True)

		self.setColumnWidth(1, 170)
		

	def registerCallbacks(self):
		if self.widgetOccelmnt is not None:
			self.widgetOccelmnt.textChanged.connect(self.textEditOccelmntChanged)
			self.widgetEventTime.dateTimeChanged.connect(self.dateTimeEventTimeChanged)
			self.widgetEventDuration.textChanged.connect(self.textEditEventDurationChanged)
			self.widgetEventUncertainty.textChanged.connect(self.textEditEventUncertaintyChanged)
			self.widgetExtraStart.textChanged.connect(self.textEditExtraStartChanged)
			self.widgetExtraEnd.textChanged.connect(self.textEditExtraEndChanged)
		self.widgetAdd.clicked.connect(self.buttonAddPressed)
		self.widgetCancel.clicked.connect(self.buttonCancelPressed)

	
	# CALLBACKS

	def buttonAddPressed(self):
		name = self.widgetName.text()
		if self.radec_format == 'hour':
			ra = float(self.widgetRA.text())
			dec = float(self.widgetDEC.text())
			coord = AstCoord.from24Deg(ra, dec, 'icrs')
		elif self.radec_format == 'hmsdms':
			ra = self.widgetRA.getValue()
			dec = self.widgetDEC.getValue()
			coord = AstCoord.fromHMS(ra, dec, 'icrs')
		elif self.radec_format == 'deg':
			ra = float(self.widgetRA.text())
			dec = float(self.widgetDEC.text())
			coord = AstCoord.from360Deg(ra, dec, 'icrs')
		if self.widgetEventTime is not None:
			event_time = self.widgetEventTime.dateTime().toString('yyyy-MM-ddThh:mm:ss')
		if self.widgetEventDuration is not None:
			event_duration = float(self.widgetEventDuration.text())
		if self.widgetEventUncertainty is not None:
			event_uncertainty = float(self.widgetEventUncertainty.text())
		if self.widgetStartTime is not None:
			start_time = self.widgetStartTime.dateTime().toString('yyyy-MM-ddThh:mm:ss')
		if self.widgetEndTime is not None:
			end_time = self.widgetEndTime.dateTime().toString('yyyy-MM-ddThh:mm:ss')

		if self.database == 'Occultations':
			if self.widgetOccelmnt is not None:
				occelmnt = self.widgetOccelmnt.toPlainText()
				if not occelmnt == '':
					pOccelmnt = self.processOccelmnt(occelmnt)
					print(pOccelmnt)
					occelmnt_dict = pOccelmnt['occelmnt_dict']
				else:
					occelmnt_dict = {}
			else:
				occelmnt_dict = self.editValues['occelmnt']

			if not self.addUpdateOccultationToOccultationDatabase(name, coord, event_time, start_time, end_time, event_duration, event_uncertainty, occelmnt_dict,  originalName = self.editValues['name'] if self.editValues is not None else None):
				return	
		else:
			occelmnt = None
			if not self.addUpdateObjectToCustomDatabase(name, coord, originalName = self.editValues['name'] if self.editValues is not None else None):
				return

		self.panel.acceptDialog()


	def buttonCancelPressed(self):
		self.panel.cancelDialog()
	

	def textEditOccelmntChanged(self):
		txt = self.widgetOccelmnt.toPlainText()
		if txt == '':
			self.widgetRA.setEnabled(True)
			self.widgetDEC.setEnabled(True)

		pOccelmnt = self.processOccelmnt(txt)
		if pOccelmnt is not None:
			print(pOccelmnt)

			self.widgetName.setText(pOccelmnt['asteroidName'])
			coord = pOccelmnt['starCoord']
			self.widgetEventTime.setDateTime(pOccelmnt['occelmntClosestApproachTime'])
			self.widgetEventDuration.setText(pOccelmnt['eventDuration'])

			if self.radec_format == 'hour':
				(ra, dec) = coord.raDec24Deg('icrs')
				self.widgetRA.setText('%0.10f' % ra)
				self.widgetDEC.setText('%0.10f' % dec)
			elif self.radec_format == 'hmsdms':
				(ra, dec) = coord.raDecHMS('icrs')
				self.widgetRA.setValue(ra[0], ra[1], ra[2])
				self.widgetDEC.setValue(dec[0], dec[1], dec[2])
			elif self.radec_format == 'deg':
				(ra, dec) = coord.raDec360Deg('icrs')
				self.widgetRA.setText('%0.10f' % ra)
				self.widgetDEC.setText('%0.10f' % dec)

			self.widgetRA.setEnabled(False)
			self.widgetDEC.setEnabled(False)
		
			self.calcStartEndRecordingTimes()


	def dateTimeEventTimeChanged(self, dateTime):
		self.calcStartEndRecordingTimes()


	def textEditEventDurationChanged(self, text):
		self.calcStartEndRecordingTimes()


	def textEditEventUncertaintyChanged(self, text):
		self.calcStartEndRecordingTimes()


	def textEditExtraStartChanged(self, text):
		self.calcStartEndRecordingTimes()


	def textEditExtraEndChanged(self, text):
		self.calcStartEndRecordingTimes()
			


	# OPERATIONS

	def setRaDec(self, coord):
		ra = ''
		dec = ''
		if coord is not None:
			(ra, dec) = coord.raDecStrForSettingFormat('icrs')

		self.widgetRA.setText(ra)
		self.widgetDEC.setText(dec)


	def messageBoxSearchObjectSuccess(self, name, coord):
		save = False
		if self.widgetDatabase.currentText() == UiPanelObject.SEARCH_SIMBAD:
			save = True

		buttons = QMessageBox.Yes | QMessageBox.No
		if save:
			msg = 'Object found, goto or save to custom?'
			buttons |= QMessageBox.Save
		else:
			msg = 'Object found, goto?'

		ret = QMessageBox.question(self, ' ', msg, buttons)
		self.widgetSearch.setModified(True)
		if ret == QMessageBox.Yes:
			return True
		elif ret == QMessageBox.Save:
			self.addUpdateObjectToCustomDatabase(name, coord)
			return False
		else:
			return False


	def messageBoxConfirmEventTime(self):
		ret = QMessageBox.question(self, ' ', "Is the event time the correct time for the event at the location you're targetting?  Are the calculated start and end times correct for automatic recording?", QMessageBox.Yes | QMessageBox.No)
		if ret == QMessageBox.Yes:
			return True
		else:
			return False


	def addUpdateObjectToCustomDatabase(self, name, coord, originalName = None):
		customObjects = Settings.getInstance().objects['custom_objects']
		if self.editValues is None:
			for object in customObjects:
				if object['name'] == name:
					self.messageBoxWriteExistsInDatabase()
					return False

		(ra, dec) = coord.raDec360Deg('icrs')
		
		# If we're updating, delete the old one
		if originalName is not None:
			for i in range(len(customObjects)):
				if customObjects[i]['name'] == originalName:
					customObjects.pop(i)
					break

		# Add the new one
		customObjects.append({"name": name, "ra": ra, "dec": dec})

		Settings.getInstance().writeSubsetting('objects')
		return True


	def calcStartEndRecordingTimes(self):
		eventCenterTime		= self.widgetEventTime.dateTime().toPyDateTime()

		try:
			eventDuration		= float(self.widgetEventDuration.text())
		except ValueError:
			eventDuration = 0.0

		try:
			eventUncertainty	= float(self.widgetEventUncertainty.text())
		except ValueError:
			eventUncertainty = 0.0

		try:
			extraStartSecs		= int(self.widgetExtraStart.text())
		except ValueError:
			extraStartSecs = 0

		try:
			extraEndSecs		= int(self.widgetExtraEnd.text())
		except ValueError:
			extraEndSecs = 0

		recordingSyncTime	= max( (self.camera.videoFrameDuration / 1000000.0) * self.camera.videoBufferCount, 12.0)
			
		startTime = eventCenterTime
		startTime -= timedelta(seconds = eventDuration / 2.0)
		startTime -= timedelta(seconds = eventUncertainty)
		startTime -= timedelta(seconds = recordingSyncTime)
		startTime -= timedelta(seconds = extraStartSecs)

		endTime	= eventCenterTime
		endTime	+= timedelta(seconds = eventDuration / 2.0)
		endTime	+= timedelta(seconds = eventUncertainty)
		endTime	+= timedelta(seconds = extraEndSecs)

		self.widgetStartTime.setDateTime(startTime)
		self.widgetEndTime.setDateTime(endTime)

		recordingDuration = (endTime - startTime).seconds
		self.widgetRecDuration.setText('%d' % recordingDuration)
		

	def processOccelmnt(self, occelmnt):
		ret = {}

		# Strip everything before <Occultations> and everything after </Occultations>
		startIndex = occelmnt.find('<Occultations>')
		endIndex = occelmnt.find('</Occultations>')
		if startIndex == -1 or endIndex == -1:
			QMessageBox.information(self, ' ', "Occelmnt doesn't start with <Occultations> and end with </Occultations>")
			return None
		endIndex += 15
		occelmnt = occelmnt[startIndex:endIndex]
		print('Occelmnt Stripped:', occelmnt)

		# Convert the xml into a dictionary
		occelmnt_dict = xmltodict.parse(occelmnt)
		print('Occelmnt dict:', occelmnt_dict)

		if isinstance(occelmnt_dict['Occultations']['Event'], list):
			QMessageBox.information(self, ' ', 'Occelmnt can only contain one Event')
			return None

		# Extract the details
		star = occelmnt_dict['Occultations']['Event']['Star'].split(',')
		ret['starName'] = star[0].strip()
		starRa = float(star[1])
		starDec = float(star[2])

		object = occelmnt_dict['Occultations']['Event']['Object'].split(',')
		ret['asteroidId'] = object[0].strip()
		ret['asteroidName'] = object[1].strip()

		elements = occelmnt_dict['Occultations']['Event']['Elements'].split(',')
		ret['eventDuration'] = elements[1].strip()
		utcTime = elements[5]
		utcHour = int(utcTime.split('.')[0])
		utcFractionalHour = float(utcTime) - float(utcHour)
		utcHourSecs = utcFractionalHour * 3600
		utcMins = int(utcHourSecs / 60)
		utcSecs = int(utcHourSecs - (utcMins * 60))	

		occelmntClosestApproachTime = '%04d-%02d-%02dT%02d:%02d:%02d' % (int(elements[2]), int(elements[3]), int(elements[4]), utcHour, utcMins, utcSecs)
		ret['occelmntClosestApproachTime'] = QDateTime().fromString(occelmntClosestApproachTime, 'yyyy-MM-ddThh:mm:ss')

		ret['starCoord'] = AstCoord.from24Deg(starRa, starDec, 'icrs')	

		ret['occelmnt_dict'] = occelmnt_dict

		return ret


	def addUpdateOccultationToOccultationDatabase(self, name, coord, event_time, start_time, end_time, event_duration, event_uncertainty, occelmnt, originalName = None) -> bool:
		occultations = Settings.getInstance().occultations['occultations']
		if self.editValues is None:
			for object in occultations:
				if object['name'] == name:
					self.messageBoxWriteExistsInDatabase()
					return False

		if not self.messageBoxConfirmEventTime():
			return False

		(ra, dec) = coord.raDec360Deg('icrs')

		# If we're updating, delete the old one
		if originalName is not None:
			for i in range(len(occultations)):
				if occultations[i]['name'] == originalName:
					occultations.pop(i)
					break

		# Add the new one
		occultations.append({"name": name, "ra": ra, "dec": dec, "event_time": event_time, "start_time": start_time, "end_time": end_time, "event_duration": event_duration, "event_uncertainty": event_uncertainty,  "occelmnt": occelmnt})

		Settings.getInstance().writeSubsetting('occultations')
		
		return True


	def messageBoxSearchObjectFailed(self):
		QMessageBox.information(self, ' ', 'Object not found !')


	def messageBoxWriteExistsInDatabase(self):
		QMessageBox.information(self, ' ', 'Object already exists in database !')


