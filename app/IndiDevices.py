import sys
import time
import logging
import PyIndi
import subprocess
from settings import Settings
import os
from astcoord import AstCoord
from signal import SIGHUP
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox


INDI_HOST			= 'localhost'
INDI_PORT			= 7624
INDI_RETRIES			= 5


class IndiDevices:

	def __init__(self, host=INDI_HOST, port=INDI_PORT):
		self.settings = Settings.getInstance().mount
		print('IndiDevice: Setting up mount as a', self.settings['name'])

		# Start mount control indiserver process
		self.killIndiServerByName()

		self.indiserver_pid = subprocess.Popen(['/usr/bin/indiserver', '-v', '-m',  '100', self.settings['indi_module']]).pid
		time.sleep(2)		# Wait for startup

		# Setup logging
		logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

		# Create connection to indi	
		self.connected		= False	
		self.indi		= IndiClient(self.updatePropertyCallback)
		self.indi.setServer(host, port)

		self.telescope		= None


	def killIndiServerByName(self):
		for line in os.popen('/usr/bin/ps -ax | grep "indiserver" | grep -v grep'):
			pid = line.split()[0]
			os.kill(int(pid), SIGHUP)
			time.sleep(2)


	def killIndiServer(self):
		print('Killing indiserver...')
		os.kill(self.indiserver_pid, SIGHUP)


	def updatePropertyCallback(self, name, typeStr, deviceName):
		if deviceName == self.settings['indi_telescope_device_id'] and self.telescope is not None:
			self.telescope.updatePropertyCallback(name, typeStr, deviceName)
			

	# Returns True if connection was successful, else false

	def connect(self, usb_tty, simulate):
		telescope_id = self.settings['indi_telescope_device_id']
		if not self.connected:
			if  not self.indi.connectServer():
				print( f"Error: indiserver not found running on {self.indi.getHost()}:{self.indi.getPort()}" )
			else:
				self.connected = True
				self.telescope = IndiTelescope(telescope_id, self.indi)

			time.sleep(1)	# Wait for devices to be discovered
	
			#self.dumpAllProperties()

		if self.telescope.connect(usb_tty, simulate):
			return True
		else:
			return False


	def disconnect(self):
		self.indi.disconnectServer()
		self.connected = False


	# Print list of devices. The list is obtained from the wrapper function getDevices as indiClient is an instance
	# of PyIndi.BaseClient and the original C++ array is mapped to a Python List. Each device in this list is an
	# instance of PyIndi.BaseDevice, so we use getDeviceName to print its actual name.

	def dumpAllProperties(self):
		print("List of devices")
		deviceList = self.indi.getDevices()
		for device in deviceList:
			print(f"   > {device.getDeviceName()}")

		# Print all properties and their associated values.
		print("List of Device Properties")
		for device in deviceList:
			print(f"-- {device.getDeviceName()}")
			genericPropertyList = device.getProperties()

		for genericProperty in genericPropertyList:
			print(f"   > {genericProperty.getName()} {genericProperty.getTypeAsString()}")

			if genericProperty.getType() == PyIndi.INDI_TEXT:
				for widget in PyIndi.PropertyText(genericProperty):
					print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getText()}")

			if genericProperty.getType() == PyIndi.INDI_NUMBER:
				for widget in PyIndi.PropertyNumber(genericProperty):
					print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getValue()}")

			if genericProperty.getType() == PyIndi.INDI_SWITCH:
				for widget in PyIndi.PropertySwitch(genericProperty):
					print(f"       {widget.getName()}({widget.getLabel()}) = {widget.getStateAsString()}")

			if genericProperty.getType() == PyIndi.INDI_LIGHT:
				for widget in PyIndi.PropertyLight(genericProperty):
					print(f"       {widget.getLabel()}({widget.getLabel()}) = {widget.getStateAsString()}")

			if genericProperty.getType() == PyIndi.INDI_BLOB:
				for widget in PyIndi.PropertyBlob(genericProperty):
					print(f"       {widget.getName()}({widget.getLabel()}) = <blob {widget.getSize()} bytes>")


def indiGetWithTimeout(func, id):
	device = None
	for i in range(INDI_RETRIES):
		device = func(id)
		if device:
			break	
		time.sleep(0.5)
	return device


class IndiTelescope:
	
	def __init__(self, device_id, indi):
		self.indi = indi
		self.device_id = device_id
		self.coord_update_callback = None
		self.tracking_update_callback = None
		self.park_update_callback = None
		self.settings = Settings.getInstance().mount
		self.lockTrackingOff = False

		# Get the telescope device called device_id
		self.device = indiGetWithTimeout(self.indi.getDevice, self.device_id)
		if self.device is None:
			print( f"Error: IndiTelescope: Unable to start indi device {self.device_id}" )
		else:
			print( f"IndiTelescope: device obtained" )

		# Get the connect mode switch
		print('Device_ID:', device_id)

		# Obtain the device name, the driver thinks it has
		deviceList = self.indi.getDevices()
		for device in deviceList:
			print('Discovered Indi Device In Driver:', device.getDeviceName())
		firstDeviceName = deviceList[0].getDeviceName()

		# Compare the device id of the drive to the device id specified in settings
		if firstDeviceName != device_id:
			result = QMessageBox.warning(None, ' ', 'Mismatch between the Indi Telescope Device Id specified in Settings/Mount and the actual device id in the driver.\n\nSettings: %s\nDriver:     %s\n\nWould you like to update the settings to match?' % (device_id, firstDeviceName), QMessageBox.Yes|QMessageBox.No)
			if result == QMessageBox.Yes:
				self.settings['indi_telescope_device_id'] = firstDeviceName
				Settings.getInstance().writeSubsetting('mount')
				QMessageBox.information(None, ' ', 'Indi Telescope Device Id has been updated to match.\n\nAstrid will now exit, start app again to pickup device change.', QMessageBox.Ok)
				raise ValueError('Quitting Astrid due to device id being changed.  This is not an error!')


		if self.settings['indi_custom_properties'] is not None and len(self.settings['indi_custom_properties']) > 0:
			for property in self.settings['indi_custom_properties'].split(';'):
				cmd = ['/usr/bin/indi_setprop', property]
				print(cmd)
				subprocess.run(args=cmd)

		self.connectionModeSwitch = self.getSwitch('CONNECTION_MODE')
		if self.connectionModeSwitch:
			if self.device_id == 'Starbook Ten':
				switches = [True]
			else:
				switches = [True, False]
			self.sendSwitch(self.connectionModeSwitch, switches)	# Set the connection on (typically serial)
			print( f"IndiTelescope: connection mode switch requested on" )


	def connect(self, usb_tty, simulate) -> bool:
		# Get and set the device port
		if simulate:
			self.simulationSwitch = self.getSwitch('SIMULATION')
			self.sendSwitch(self.simulationSwitch, [True, False])
		else:
			if self.device_id != 'Starbook Ten':
				self.tdevice_port = self.getText('DEVICE_PORT')
				if self.tdevice_port:
					self.sendText(self.tdevice_port, [usb_tty])
					print( f"IndiTelescope: usb_tty set" )
		
		if self.device_id != 'Starbook Ten':
			# Set the Baud Rate
			device_baud_rate = self.getSwitch('DEVICE_BAUD_RATE')
			if device_baud_rate:
				switchList = []
				for i in range(0, len(device_baud_rate)):
					if str(self.settings['baud']) == device_baud_rate[i].getName():
						switchList.append(True)
					else:
						switchList.append(False)
				print(switchList)
				self.sendSwitch(device_baud_rate, switchList)
			else:
				print('Error: IndiTelescope: baud rate switch not found')
	
		self.connectionSwitch		= self.getSwitch('CONNECTION')

		if self.device.isConnected():
			print( f"IndiTelescope: we are already connected" )
		else:
			# We need to connect before we can access the other settings
			self.sendSwitch(self.connectionSwitch, [True, False])
			print( f"IndiTelescope: connection switch requested on" )

			time.sleep(2)	# Wait for connection
			if not self.device.isConnected():
				print('Error: IndiTelescope: unable to connect on:', usb_tty)
				return False

		self.geographic_coord		= self.getNumber('GEOGRAPHIC_COORD')
		self.goHomeSwitch		= self.getSwitch('GO_HOME')
		self.park_state			= self.getSwitch('TELESCOPE_PARK')
		self.time_utc			= self.getText('TIME_UTC')
		self.on_coord_set		= self.getSwitch('ON_COORD_SET')
		self.equatorial_eod_coord	= self.getNumber('EQUATORIAL_EOD_COORD')
		self.telescope_track_state	= self.getSwitch('TELESCOPE_TRACK_STATE')
		self.telescope_pier_side	= self.getSwitch('TELESCOPE_PIER_SIDE')
		self.abortMotionSwitch		= self.getSwitch('TELESCOPE_ABORT_MOTION')
		self.slew_rate_switch		= self.getSwitch('TELESCOPE_SLEW_RATE')
		self.telescope_motion_ns	= self.getSwitch('TELESCOPE_MOTION_NS')
		self.telescope_motion_we	= self.getSwitch('TELESCOPE_MOTION_WE')
		self.telescope_track_mode	= self.getSwitch('TELESCOPE_TRACK_MODE')

		self.setMaxSlewRate()
		
		return True


	def getText(self, propertyName):
		ret = indiGetWithTimeout(self.device.getText, propertyName)
		if ret:
			print('IndiTelescope: %s obtained' % propertyName)
		else:
			print('Error: IndiTelescope: Unable to obtain %s from indi device %s' % (propertyName, self.device_id))
		return ret


	def getSwitch(self, propertyName):
		ret = indiGetWithTimeout(self.device.getSwitch, propertyName)
		if ret:
			print('IndiTelescope: %s obtained' % propertyName)
		else:
			print('Error: IndiTelescope: Unable to obtain %s from indi device %s' % (propertyName, self.device_id))
		return ret


	def getNumber(self, propertyName):
		ret = indiGetWithTimeout(self.device.getNumber, propertyName)
		if ret:
			print('IndiTelescope: %s obtained' % propertyName)
		else:
			print('Error: IndiTelescope: Unable to obtain %s from indi device %s' % (propertyName, self.device_id))
		return ret


	def sendSwitch(self, sswitch, switches: list):
		"""
			sswitch is the switch object, e.g. self.goHomeSwitch
			switches is an array of bools, one for each property
			Returns True on success, False on failure
		"""
		if sswitch:
			for stateIndex in range(0, len(switches)):
				sswitch[stateIndex].setState(PyIndi.ISS_ON if switches[stateIndex] else PyIndi.ISS_OFF)
				if self.settings['debug']:
					print('IndiTelescope: SET %s.%s=%s' % ( sswitch.getName(), sswitch[stateIndex].getName(), sswitch[stateIndex].getStateAsString()) )
			self.indi.sendNewProperty(sswitch)
			return True
		return False


	def sendText(self, stext, texts: list):
		"""
			stext is the text object, e.g. self.time_utc
			texts is an array of strings, one for each property
			Returns True on success, False on failure
		"""
		if stext:
			for stateIndex in range(0, len(texts)):
				stext[stateIndex].setText(texts[stateIndex])
				if self.settings['debug']:
					print('IndiTelescope: SET %s.%s=%s' % ( stext.getName(), stext[stateIndex].getName(), stext[stateIndex].getText()) )
			self.indi.sendNewProperty(stext)
			return True
		return False


	def sendValue(self, svalue, values: list):
		"""
			svalue is the value object, e.g. self.geographic_coord
			values is an array of values, one for each property
			Returns True on success, False on failure
		"""
		if svalue:
			for stateIndex in range(0, len(values)):
				svalue[stateIndex].setValue(values[stateIndex])
				if self.settings['debug']:
					print('IndiTelescope: SET %s.%s=%s' % ( svalue.getName(), svalue[stateIndex].getName(), svalue[stateIndex].getValue()) )
			self.indi.sendNewProperty(svalue)
			return True
		return False


	def setSite(self, lat, lon, alt):
		if self.settings['set_site']:
			self.sendValue(self.geographic_coord, [lat, lon, alt])
			print( f"IndiTelescope: site set" )


	# timenow = datetime.utcnow()
	# local_offset should be in the format -6.00 (string)
	# local_offset is not really relevant, as we are in UTC time.  It's only seems to be relevant when we set the mount time via
	# an app where the local time of the device is used, set to 0.0

	def setTime(self, time_now, local_offset):
		if self.settings['set_time']:
			self.sendText(self.time_utc, [time_now.strftime("%Y-%m-%dT%H:%M:%S"), local_offset])


	def goHome(self):
		self.sendSwitch(self.goHomeSwitch, [True])


	def park(self, enable):
		self.sendSwitch(self.park_state, [enable, not enable] )


	def goto(self, icrs_coord, already_in_mount_native=False, no_tracking = False, slewCompleteCallback = None):
		self.slewCompleteCallback = slewCompleteCallback

		# Although we could set tracking to off as part of the slew, some mounts would comply and some wouldn't,
		# and we also need to detect the switch back to Tracking to indicate the slew is complete, so we enable tracking and then switch
		# if off afterwards via lockTrackingOff if needed
		values = [True, False, False]	# Set state to TRACK (which is SLEW and then TRACK)
		if no_tracking:
			self.lockTrackingOff = True
		else:
			self.lockTrackingOff = False
		self.sendSwitch(self.on_coord_set, values)


		# We set the desired coordinates
		if not self.settings['mount_is_j2000'] and not already_in_mount_native:
			(ra, dec) = icrs_coord.raDec24Deg('icrs', jnow=True)
		else:
			(ra, dec) = icrs_coord.raDec24Deg('icrs')
		self.sendValue(self.equatorial_eod_coord, [ra, dec])


	def sync(self, icrs_coord):
		self.sendSwitch(self.on_coord_set, [False, False, True])	# Set state to SYNC

		#time.sleep(1.0)

		# We set the desired coordinates
		if self.settings['mount_is_j2000']:
			(ra, dec) = icrs_coord.raDec24Deg('icrs')
		else:
			(ra, dec) = icrs_coord.raDec24Deg('icrs', jnow=True)
		self.sendValue(self.equatorial_eod_coord, [ra, dec])


	def tracking(self, enable):
		if self.settings['tracking_capable']:
			self.sendSwitch(self.telescope_track_state, [enable, not enable])


	def abortMotion(self):
		self.sendSwitch(self.abortMotionSwitch, [True])	# Abort motion and stop


	# if west is True, pier side is west (regular)
	# if west is False, pier side is east (inverted)
	# Reference: https://www.cloudynights.com/topic/794278-understanding-mounts-pier-side-eastwest-using-ascom-drivers/ 

	def pierSide(self, west):
		self.sendSwitch(self.telescope_pier_side, [west, not west])	# Abort motion and stop


	def getSlewRateList(self):
		slewRates = []

		if not self.slew_rate_switch:
			return slewRates

		for i in range(0, len(self.slew_rate_switch)):
			name = self.slew_rate_switch[i].getName()
			if len(name) > 0 and name[-1] == 'x':
				slewRates.append(self.slew_rate_switch[i].getName())

		return slewRates


	def getSlewRateIndex(self):
		slewRates = self.getSlewRateList()
		if len(slewRates) > 0:
			onSwitchIndex = self.slew_rate_switch.findOnSwitchIndex()	
			name = self.slew_rate_switch[onSwitchIndex].getName()
			return slewRates.index(name)	
		return 0
		

	# slewRateName = 1x, 2x etc.
	def setSlewRate(self, slewRateName):
		switchList = []
		for i in range(0, len(self.slew_rate_switch)):
			if slewRateName == self.slew_rate_switch[i].getName():
				switchList.append(True)
			else:
				switchList.append(False)
		self.sendSwitch(self.slew_rate_switch, switchList)
		

	def setMaxSlewRate(self):
		slewRates = self.getSlewRateList()
		if len(slewRates) > 0:
			self.setSlewRate(slewRates[-1])


	"""
	north_south = north(1), south(-1), none(0)
	west_east   = west(1), east(-1), none(0)
	"""
	def setManualMotion(self, north_south, west_east):
		if north_south == 1:
			nslist = [True, False]
		elif north_south == -1:
			nslist = [False, True]
		else:
			nslist = [False, False]
		self.sendSwitch(self.telescope_motion_ns, nslist)

		if west_east == 1:
			welist = [True, False]
		elif west_east == -1:
			welist = [False, True]
		else:
			welist = [False, False]
		self.sendSwitch(self.telescope_motion_we, welist)


	
	"""
	mode can be one of 'sidereal', 'solar', 'lunar', 'custom'
	
	"""
	def setTrackMode(self, mode):
		modelist = [False, False, False, False]
		modes = ['sidereal', 'solar', 'lunar', 'custom']
		modelist[modes.index(mode)] = True
		self.sendSwitch(self.telescope_track_mode, modelist)


	def getTrackMode(self):
		onSwitchIndex = self.telescope_track_mode.findOnSwitchIndex()	
		modes = ['sidereal', 'solar', 'lunar', 'custom']
		return modes[onSwitchIndex]


	def updatePropertyCallback(self, name, typeStr, deviceName):
		if self.settings['debug']:
			if   typeStr == 'INDI_NUMBER':
				prop = indiGetWithTimeout(self.device.getNumber, name)
			elif typeStr == 'INDI_SWITCH':
				prop = indiGetWithTimeout(self.device.getSwitch, name)
			elif typeStr == 'INDI_TEXT':
				prop = indiGetWithTimeout(self.device.getText, name)
			elif typeStr == 'INDI_LIGHT':
				prop = indiGetWithTimeout(self.device.getLight, name)
			else:
				prop = None
				print('Error: IndiTelescope: Unknown Type: %s for property %s' % (typeStr, name))

			if prop is None:
				print('Error: IndiTelescope: Unable to obtain %s from indi device %s' % (name, self.device_id))
			else:
				if   typeStr == 'INDI_SWITCH':
					for subProp in prop:
						print('IndiTelescope: UPDATE %s.%s=%s' % (prop.getName(), subProp.getName(), subProp.getStateAsString()))
				elif typeStr == 'INDI_TEXT':
					for subProp in prop:
						print('IndiTelescope: UPDATE %s.%s=%s' % (prop.getName(), subProp.getName(), subProp.getText()))
				elif typeStr == 'INDI_NUMBER':
					for subProp in prop:
						print('IndiTelescope: UPDATE %s.%s=%s' % (prop.getName(), subProp.getName(), subProp.getValue()))
				elif typeStr == 'INDI_LIGHT':
					for subProp in prop:
						print('IndiTelescope: UPDATE %s.%s=%s' % (prop.getName(), subProp.getName(), subProp.getStateAsString()))
				else:
					print('Error: IndiTelescope: Urecognized typeStr')

		if name == 'EQUATORIAL_EOD_COORD' and self.coord_update_callback is not None:
			(ra, dec) = (self.equatorial_eod_coord[0].getValue(), self.equatorial_eod_coord[1].getValue())
			coord = AstCoord.from24Deg(ra, dec, 'icrs')
			self.coord_update_callback(coord)
		if name == 'TELESCOPE_TRACK_STATE' and self.tracking_update_callback is not None:
			if self.settings['tracking_capable']:
				tracking_enabled = self.telescope_track_state[0].getState()
				self.tracking_update_callback(tracking_enabled)
				if tracking_enabled and self.lockTrackingOff:

					if self.slewCompleteCallback is not None:
						self.slewCompleteCallback()
						self.slewCompleteCallback = None
					self.sendSwitch(self.telescope_track_state, [False, True])
			else:
				# If tracking should be off, switch it off (normally needed to non goto/tracking mounts
				self.sendSwitch(self.telescope_track_state, [False, True])
		if name == 'TELESCOPE_PARK' and self.park_update_callback is not None:
			self.park_update_callback(self.park_state[0].getState())


	def setCoordUpdateCallback(self, callback):
		self.coord_update_callback = callback

		# Get the current mount position and update the ui
		(ra, dec) = (self.equatorial_eod_coord[0].getValue(), self.equatorial_eod_coord[1].getValue())
		coord = AstCoord.from24Deg(ra, dec, 'icrs')
		self.coord_update_callback(coord)


	def setTrackingUpdateCallback(self, callback):
		self.tracking_update_callback = callback
		self.tracking_update_callback(self.telescope_track_state[0].getState())


	def setParkUpdateCallback(self, callback):
		self.park_update_callback = callback
		self.park_update_callback(self.park_state[0].getState())


	def getTracking(self):
		if self.settings['tracking_capable']:
			return True if self.telescope_track_state[0].getState() else False
		else:
			return False


	def getPark(self):
		return True if (self.park_state is not None and self.park_state[0].getState()) else False


# The IndiClient class which inherits from the module PyIndi.BaseClient class
# Note that all INDI constants are accessible from the module as PyIndi.CONSTANTNAME
# Reference: https://github.com/indilib/pyindi-client

class IndiClient(PyIndi.BaseClient):

	def __init__(self, updatePropertyCallback):
		super(IndiClient, self).__init__()
		self.logger = logging.getLogger("IndiClient")
		self.logger.info("creating an instance of IndiClient")
		self.updatePropertyCallback = updatePropertyCallback


	def newDevice(self, d):
		"""Emmited when a new device is created from INDI server."""
		self.logger.info(f"new device {d.getDeviceName()}")


	def removeDevice(self, d):
		"""Emmited when a device is deleted from INDI server."""
		self.logger.info(f"remove device {d.getDeviceName()}")


	def newProperty(self, p):
		"""Emmited when a new property is created for an INDI driver."""
		self.logger.info(f"new property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")


	def updateProperty(self, p):
		"""Emmited when a new property value arrives from INDI server."""
		#self.logger.info(f"update property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")
		self.updatePropertyCallback(p.getName(), p.getTypeAsString(), p.getDeviceName())

	def removeProperty(self, p):
		"""Emmited when a property is deleted for an INDI driver."""
		self.logger.info(f"remove property {p.getName()} as {p.getTypeAsString()} for device {p.getDeviceName()}")


	def newMessage(self, d, m):
		"""Emmited when a new message arrives from INDI server."""
		self.logger.info(f"new Message {d.messageQueue(m)}")


	def serverConnected(self):
		"""Emmited when the server is connected."""
		self.logger.info(f"Server connected ({self.getHost()}:{self.getPort()})")


	def serverDisconnected(self, code):
		"""Emmited when the server gets disconnected."""
		self.logger.info(f"Server disconnected (exit code = {code},{self.getHost()}:{self.getPort()})")
