from processlogger import ProcessLogger
from UiPanel import UiPanel
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QApplication
from astropy import units as u
from astropy.coordinates import SkyCoord
from settings import Settings
from astcoord import AstCoord
from astropy.coordinates.name_resolve import NameResolveError
from UiPanelObjectAddEdit import UiPanelObjectAddEdit
from UiPanelObjectList import UiPanelObjectList
from UiPanelPrepoint import UiPanelPrepoint
from UiPanelAutoRecord import UiPanelAutoRecord
from PyQt5.QtCore import Qt
from UiDialogPanel import UiDialogPanel
from UiPanelAutoRecording import UiPanelAutoRecording
from datetime import datetime, timedelta
from astsite import AstSite
from pathcomputation import PathComputation
from owcloud import OWCloud
import math



class UiPanelObject(UiPanel):
	# Initializes and displays a Panel

	SEARCH_SIMBAD		= 'SIMBAD (online)'
	SEARCH_CUSTOM		= 'Custom'
	SEARCH_OCCULTATIONS	= 'Occultations'

	MOON_MULTIPLIER = 10.0  # Multiplier for detecting moons, this gets multiplied by the event duration

	def __init__(self, camera):
		super().__init__('Object (ICRS)')
		self.processLogger = ProcessLogger.getInstance()
		self.logger = self.processLogger.getLogger()
		self.camera		= camera
		self.occultationObject	= None
		self.widgetDatabase	= self.addComboBox('Database', [UiPanelObject.SEARCH_SIMBAD, UiPanelObject.SEARCH_CUSTOM, UiPanelObject.SEARCH_OCCULTATIONS])
		self.widgetDatabase.setObjectName('comboBoxDatabase')
		self.widgetSearch	= self.addLineEdit('Search')
		self.widgetRA		= self.addLineEditDouble('RA', 0.0, 24.0, 10, editable=False)
		self.widgetDEC		= self.addLineEditDouble('DEC', -90.0, 90.0, 10, editable=False)
		self.widgetEventTime    = self.addLineEdit('Event Time', editable=False)
		self.widgetChord    	= self.addLineEdit('Chord Dist', editable=False)
		self.hideWidget(self.widgetEventTime)
		self.hideWidget(self.widgetChord)
		self.widgetPrepoint	= self.addButton('Prepoint', True)
		self.widgetAutoRecord	= self.addButton('Auto Record', True)
		self.hideWidget(self.widgetPrepoint)
		self.widgetAdd		= self.addButton('Add', True)
		self.widgetList		= self.addButton('List', True)
		self.hideWidget(self.widgetAdd)
		self.hideWidget(self.widgetList)

		# Set to Occultations by default
		self.widgetDatabase.setCurrentText(UiPanelObject.SEARCH_OCCULTATIONS)
		self.comboBoxDatabaseChanged(self.widgetDatabase.currentText())
		
		self.setColumnWidth(0, 75)
		self.setColumnWidth(1, 170)


	def registerCallbacks(self):
		self.widgetDatabase.currentTextChanged.connect(self.comboBoxDatabaseChanged)
		self.widgetSearch.editingFinished.connect(self.lineEditSearchChanged)
		self.widgetPrepoint.clicked.connect(self.buttonPrepointPressed)
		self.widgetAutoRecord.clicked.connect(self.buttonAutoRecordPressed)
		self.widgetAdd.clicked.connect(self.buttonAddPressed)
		self.widgetList.clicked.connect(self.buttonListPressed)

	
	# CALLBACKS

	def comboBoxDatabaseChanged(self, text):
		self.camera.clearObject()
		if   text == UiPanelObject.SEARCH_SIMBAD:
			self.hideWidget(self.widgetEventTime)
			self.hideWidget(self.widgetChord)
			self.hideWidget(self.widgetPrepoint)
			self.hideWidget(self.widgetAutoRecord)
			self.hideWidget(self.widgetAdd)
			self.hideWidget(self.widgetList)
		elif text == UiPanelObject.SEARCH_CUSTOM:
			self.hideWidget(self.widgetEventTime)
			self.hideWidget(self.widgetChord)
			self.hideWidget(self.widgetPrepoint)
			self.hideWidget(self.widgetAutoRecord)
			self.showWidget(self.widgetAdd)
			self.showWidget(self.widgetList)
		elif text == UiPanelObject.SEARCH_OCCULTATIONS:
			self.showWidget(self.widgetEventTime)
			self.showWidget(self.widgetChord)
			self.hideWidget(self.widgetPrepoint)
			self.hideWidget(self.widgetAutoRecord)
			self.showWidget(self.widgetAdd)
			self.showWidget(self.widgetList)
		else:
			raise ValueError('Database not valid')


	def lineEditSearchChanged(self):
		# When a message box is launch during a line edit handler, the line edit loses focus,
		# casuing 2 editingFinished messages to be sent, using isModified to prevent double launching
		if self.widgetSearch.isModified():
			self.launchSearch()


	def buttonAddPressed(self):
		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Question)
		msgBox.setText('How would you like to Add an occultation?')
		msgBox.addButton('Manual Entry or Occelmnt', QMessageBox.AcceptRole)
		msgBox.addButton('Import From OWCloud', QMessageBox.AcceptRole)
		msgBox.setStandardButtons(QMessageBox.Cancel)
		
		ret = msgBox.exec()

		if   ret == 0:
			self.dialog = UiDialogPanel('Add Object (ICRS)', UiPanelObjectAddEdit, args = {'database': self.widgetDatabase.currentText(), 'camera': self.camera, 'editValues': None}, parent = self.camera.ui)
		elif ret == 1:
			ret2 = QMessageBox.information(self, ' ', 'To import from OWCloud, the following are required:\n\n    1. Internet Connection\n    2. Valid OWCloud login/password in settings/observer\n    3. Site(s) added to events in OWCloud\n\nNote 1: Currently there is no Occelmnt information available via the OWCloud API, so Chord Distance and Event Time are not automatically updated according to the site location in Astrid. If you require this feature, please add the event manually and copy and paste the occelmnt.\n\nNote 2: After registering a site on OWCloud, it may take a few minutes for the data to be downloadble.\n\nTHIS WILL REPLACE OCCULTATIONS WITH THE SAME NAME/STATION', QMessageBox.Ok | QMessageBox.Cancel)
			if ret2 == QMessageBox.Ok:
				self.importFromOWCloud()



	def buttonListPressed(self):
		self.dialog = UiDialogPanel('List Objects - ' + self.widgetDatabase.currentText(), UiPanelObjectList, args = {'database': self.widgetDatabase.currentText(), 'camera': self.camera, 'selectListCallback': self.listSelect, 'editListCallback': self.editSelect}, parent = self.camera.ui)


	def buttonPrepointPressed(self):
		if not self.camera.isPhotoMode():
			self.camera.ui.panelTask.switchModeTo('Photo')
		self.dialog = UiDialogPanel('Prepoint', UiPanelPrepoint, args = {'camera': self.camera, 'object': self.occultationObject}, parent = self.camera.ui)


	def buttonAutoRecordPressed(self):
		if not self.camera.isOTEVideoMode():
			ret = QMessageBox.question(self, ' ', 'Auto Recording is only available when camera is in OTE Video Mode. Switch Mode To OTE Video?', QMessageBox.Yes | QMessageBox.Cancel)
			if ret == QMessageBox.Yes:
				self.camera.ui.panelTask.switchModeTo('OTE Video')
			else:
				return
		
		if self.camera.isOTEVideoMode():
			if self.camera.ui.videoFrameRateWarning():
				return

			self.dialog = UiDialogPanel('Auto Record OTE', UiPanelAutoRecord, args = {'camera': self.camera, 'object': self.occultationObject}, parent = self.camera.ui)
			if self.dialog.result() == 1:
				start_time = self.dialog.dialog.panel.start_time
				end_time = self.dialog.dialog.panel.end_time
				event_time = datetime.strptime(self.occultationObject['event_time'], '%Y-%m-%dT%H:%M:%S')
				if start_time <= datetime.utcnow():
                        		QMessageBox.warning(self, ' ', 'Start time is before now, old event, unable to record!', QMessageBox.Ok)
				else:
					self.dialog = UiDialogPanel('Auto Recording', UiPanelAutoRecording, args = {'start_time': start_time, 'end_time': end_time, 'event_time': event_time, 'camera': self.camera}, parent = self.camera.ui, modal = True)


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

		gotoCapable = Settings.getInstance().mount['goto_capable']

		if gotoCapable:
			buttons = QMessageBox.Yes | QMessageBox.No
			if save:
				buttons |= QMessageBox.Save
		else:
			if save:
				buttons = QMessageBox.Yes | QMessageBox.No
			else:
				buttons = QMessageBox.Ok

		if save:
			if gotoCapable:
				msg = 'Object found, goto or save to custom?'
			else:
				msg = 'Object found, save to custom?'
		else:
			if gotoCapable:
				msg = 'Object found, goto?'
			else:
				msg = 'Object found'

		ret = QMessageBox.question(self, ' ', msg, buttons)
		self.widgetSearch.setModified(True)
		if ret == QMessageBox.Yes:
			if not gotoCapable and save:
				self.addObjectToCustomDatabase(name, coord)
				return False
			return True
		elif ret == QMessageBox.Save:
			self.addObjectToCustomDatabase(name, coord)
			return False
		elif ret == QMessageBox.Ok:
			return True
		elif ret == QMessageBox.No:
			if gotoCapable:
				return False
			else:
				return True
		else:
			return False


	def addObjectToCustomDatabase(self, name, coord):
		customObjects = Settings.getInstance().objects['custom_objects']
		for object in customObjects:
			if object['name'] == name:
				self.messageBoxWriteCustomFailed()
				return

		(ra, dec) = coord.raDec360Deg('icrs')
		customObjects.append({"name": name, "ra": ra, "dec": dec})
		Settings.getInstance().writeSubsetting('objects')
		

	def messageBoxSearchObjectFailed(self):
		QMessageBox.information(self, ' ', 'Object not found !')


	def messageBoxWriteCustomFailed(self):
		QMessageBox.information(self, ' ', 'Object already exists in custom !')


	def findObject(self, search):
		text = self.widgetDatabase.currentText()
		if   text == UiPanelObject.SEARCH_SIMBAD:
			return self.findSimbadObject(search)
		elif text == UiPanelObject.SEARCH_CUSTOM:
			return self.findCustomObject(search)
		elif text == UiPanelObject.SEARCH_OCCULTATIONS:
			return self.findOccultationObject(search)
		else:
			raise ValueError('Database not valid')


	def findSimbadObject(self, search):
		""" Returns AstCoord, or None if not found """
		obj = None

		self.camera.ui.indeterminateProgressBar(True)

		# Because we're not processing Qt events during the simbad request cos app.exec() isn't being run during
		app = QApplication.instance()
		app.processEvents()
		app.processEvents()

		try:
			coord_icrs = SkyCoord.from_name(search, frame='icrs')
			obj = AstCoord.from360Deg(coord_icrs.ra.value, coord_icrs.dec.value, 'icrs')
		except NameResolveError:
			print("Unable to find object")
			pass
		except Exception as e:
			print("Error: simbad error:", e)
			pass

		self.camera.ui.indeterminateProgressBar(False)

		return obj


	def findCustomObject(self, search):
		""" Returns AstCoord, or None if not found """
		obj = None
		customObjects = Settings.getInstance().objects['custom_objects']
		for object in customObjects:
			if object['name'].lower() == search.lower():
				obj = AstCoord.from360Deg(object['ra'], object['dec'], 'icrs')
				break
		return obj


	def findOccultationObject(self, search):
		""" Returns AstCoord, or None if not found """
		obj = None
		self.occultationObject = None
		customObjects = Settings.getInstance().occultations['occultations']
		for object in customObjects:
			if object['name'].lower() == search.lower():
				obj = AstCoord.from360Deg(object['ra'], object['dec'], 'icrs')
				chordDist = self.verifyEventTime(object)
				self.widgetEventTime.setText(object['event_time'])

				if chordDist is None:
					self.widgetChord.setText('Not Found')
				else:
					self.widgetChord.setText('%0.3f km' % (chordDist/1000.0))

				self.occultationObject = object
				break

		if obj is not None:
			self.showWidget(self.widgetPrepoint)
			self.showWidget(self.widgetAutoRecord)

		return obj


	def setEnabledUi(self, enable):
		self.widgetDatabase.setEnabled(enable)
		self.widgetSearch.setEnabled(enable)
		self.widgetRA.setEnabled(enable)
		self.widgetDEC.setEnabled(enable)
		self.widgetAdd.setEnabled(enable)


	def launchSearch(self):
		self.widgetSearch.setModified(False)
		txt = self.widgetSearch.text()
		self.camera.searchObject(txt)


	def listSelect(self, item):
		self.widgetSearch.setText(item)
		self.launchSearch()


	def editSelect(self, item):
		editValues = None

		text = self.widgetDatabase.currentText()

		if text == UiPanelObject.SEARCH_CUSTOM:
			objects = Settings.getInstance().objects['custom_objects']
		elif text == UiPanelObject.SEARCH_OCCULTATIONS:
			objects = Settings.getInstance().occultations['occultations']

		for object in objects:
			if object['name'] == item:
				editValues = object
				break
		
		self.dialog = UiDialogPanel('Edit Object (ICRS)', UiPanelObjectAddEdit, args = {'database': self.widgetDatabase.currentText(), 'camera': self.camera, 'editValues': editValues}, parent = self.camera.ui)

	
	def __convertStrTimeToDateTime(self, sTime):
		return datetime.strptime(sTime, '%Y-%m-%dT%H:%M:%S')

	def __convertDateTimeToStrTime(self, dt):
		return dt.strftime("%Y-%m-%dT%H:%M:%S")

	def verifyEventTime(self, object):
		if not ('occelmnt' in object) or len(object['occelmnt'].keys()) == 0:
			self.logger.info('No occelmnt data recorded in the occulation, unable to verify event time or chord')
			return None

		pathComp		= PathComputation(object['occelmnt'])
		timeAndChordForLoc	= pathComp.getTimeAndChordDistanceForLocation(AstSite.lat, AstSite.lon, AstSite.alt)

		if timeAndChordForLoc is None:
			self.logger.info('No Chord because star is not visible')
			return None
		else:
			database_eventTime = self.__convertStrTimeToDateTime(object['event_time'])
			database_startTime = self.__convertStrTimeToDateTime(object['start_time'])
			database_endTime   = self.__convertStrTimeToDateTime(object['end_time'])

			deltaTimeSeconds = (timeAndChordForLoc[0] - database_eventTime).total_seconds()
			self.logger.info('Time: %s Distance: %0.4f km' % (str(timeAndChordForLoc[0]), timeAndChordForLoc[1] / 1000.0) )

			if abs(deltaTimeSeconds) >= 1:
				ret = QMessageBox.question(self, ' ', 'Event Center Time for this location differs from the one stored by %d seconds, do you wish to update start/center/end times to match?' % deltaTimeSeconds, QMessageBox.Yes | QMessageBox.No)
				if ret == QMessageBox.Yes:
					database_eventTime += timedelta(seconds=deltaTimeSeconds)
					database_startTime += timedelta(seconds=deltaTimeSeconds)
					database_endTime   += timedelta(seconds=deltaTimeSeconds)

					object['event_time'] = self.__convertDateTimeToStrTime(database_eventTime)
					object['start_time'] = self.__convertDateTimeToStrTime(database_startTime)
					object['end_time']   = self.__convertDateTimeToStrTime(database_endTime)

					db = 'occultations'
					all_occultations = Settings.getInstance().occultations['occultations']
					for o in all_occultations:
						if o['name'] == object['name']:
							o['event_time'] = object['event_time']
							o['start_time'] = object['start_time']
							o['end_time']   = object['end_time']
							Settings.getInstance().writeSubsetting(db)
							self.logger.info('updated %s' % (o['name']))
							break

		return timeAndChordForLoc[1]


	def importFromOWCloud(self):
		owcloud = OWCloud()
		(events, error) = owcloud.getEvents()

		if error is not None:
			QMessageBox.warning(self, ' ', 'Failed to download from OWCloud: %s' % error, QMessageBox.Ok)
		elif events is None:
			QMessageBox.warning(self, ' ', 'Events = None from OWCloud', QMessageBox.Ok)
		else:
			imported_count = 0

			occultations = Settings.getInstance().occultations['occultations']

			for event in events:
				name		= event['Object']
				ra		= (event['RAJ2000Hours'] / 24.0) * 360.0
				dec		= event['DEJ2000Deg']	
				eventDuration	= event['MaxDurSec']
	
				for station in event['Stations']:
					if station['IsOwnStation']:
						eventTime		= station['EventTimeUtc']
						eventUncertainty	= station['ErrorInTimeSec']
						stationName		= station['StationName']

						extraSecs		= int(math.ceil(eventDuration * UiPanelObjectAddEdit.MOON_MULTIPLIER))
						extraStartSecs		= extraSecs
						extraEndSecs		= extraSecs

						eventCenterTime = datetime.strptime(eventTime.split('.')[0], '%Y-%m-%dT%H:%M:%S')
				
						# Calculate the Start/End Times
						startTime = eventCenterTime
						startTime -= timedelta(seconds = eventDuration / 2.0)
						startTime -= timedelta(seconds = eventUncertainty)
						startTime -= timedelta(seconds = extraStartSecs)

						endTime = eventCenterTime
						endTime += timedelta(seconds = eventDuration / 2.0)
						endTime += timedelta(seconds = eventUncertainty)
						endTime += timedelta(seconds = extraEndSecs)

						eventCenterTime	= eventCenterTime.strftime("%Y-%m-%dT%H:%M:%S")
						startTime	= startTime.strftime("%Y-%m-%dT%H:%M:%S")
						endTime		= endTime.strftime("%Y-%m-%dT%H:%M:%S")
	
						occultation = { 'name': name + '-' + stationName, 'ra': ra, 'dec': dec, 'event_time': eventCenterTime, 'start_time': startTime, 'end_time': endTime, 'event_duration': eventDuration, 'event_uncertainty': eventUncertainty, 'occelmnt': {} }

						# If the occultation already exists, delete it first
						for i in range(len(occultations)):
							if occultations[i]['name'] == occultation['name']:
								occultations.pop(i)
								break

						# Add the occultation
						occultations.append(occultation)

						imported_count += 1

						print(occultation)

			if imported_count > 0:
				Settings.getInstance().writeSubsetting('occultations')

			QMessageBox.information(self, ' ', 'Imported %d registered events/stations from OWCloud' % imported_count, QMessageBox.Ok)
				
		owcloud = None
