from processlogger import ProcessLogger
import random
import ospi
import sys
import struct
import signal
import RPi.GPIO as GPIO
import queue    # imported for using queue.Empty exception
from datetime import datetime, timedelta



FRAME_INTERRUPT_GPIO			= 13
OSPI_SPEED_HZ				= 2000000
OSPI_START_DELAY			= 15

OTESTAMPER_RETRIES			= 4

# List of commands: Tuple(CommandCode, Length)
CMD_ID_MAGIC_NUMBER                     = (0x70, 0x04)
CMD_FIRMWARE_VERSION                    = (0x71, 0x02)
CMD_LED_ON                              = (0x72, 0x00)
CMD_LED_OFF                             = (0x73, 0x00)
CMD_FAN_ON                              = (0x74, 0x00)
CMD_FAN_OFF                             = (0x75, 0x00)
CMD_TIMING_TEST_ON                      = (0x76, 0x00)
CMD_TIMING_TEST_OFF                     = (0x77, 0x00)
CMD_COLD_RESTART_GPS                    = (0x78, 0x00)
CMD_FRAME_TIMING_INFO_INTERRUPT_ON      = (0x79, 0x00)
CMD_FRAME_TIMING_INFO_INTERRUPT_OFF     = (0x7A, 0x00)
CMD_BUZZER_ON                           = (0x7B, 0x00)
CMD_BUZZER_OFF                          = (0x7C, 0x00)
CMD_GPS_INFO                            = (0x90, 0x1C)
CMD_FRAME_TIMING_INFO                   = (0x91, 0x10)
CMD_CONFIRM_FRAME_RECEIVED              = (0x92, 0x00)
CMD_TEST_FRAME_FOR_VALIDATION           = (0x93, 0x10)


class ProcessOteStamper:

	OTESTAMPER_ID   = 0xFD032A1C

	XVS_END_FRAME_OFFSET_NS = 59075

	def __init__(self):
		self.connected = False
		self.recording = False


	def __cleanup_handler(self, sig, frame):
		"""
			Called to cleanup when the process exits
		"""
		if self.recording:
			self.__sendCmd(CMD_FRAME_TIMING_INFO_INTERRUPT_OFF)
			GPIO.remove_event_detect(FRAME_INTERRUPT_GPIO)

		self.__queue_clear(self.queue_frameInfo)
		self.__queue_clear(self.queue_gpsInfo)
		self.__queue_clear(self.queue_cmd)

		ospi.close()
		GPIO.cleanup()
		self.logger.info('ProcessOteStamper terminated!')
		sys.exit(0)


	# Sends a command and returns a tuple(success, data)

	def __sendCmd(self, cmd, log=True):
		(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(cmd[0], cmd[1], OTESTAMPER_RETRIES)
		if success:
			if log:
				self.logger.debug('command success:0x%02X retries:%d executionTime:%dus failHardware:%d failCrc:%d' % (cmd[0], retries, execution_time_us, fail_hardware_tx, fail_crc))
		else:
			self.logger.critical('command failed:0x%02X retries:%d executionTime:%dus failHardware:%d failCrc:%d' % (cmd[0], retries, execution_time_us, fail_hardware_tx, fail_crc))
		return (success, data)


	def __frameInterrupt(self, channel):
		"""
			Called everytime a frame interrupt occurs signalling that information about the timing of the frame is ready to
			be read. __frameInterrupt reads this information and places it on the queue_frameInfo queue.  frameInfo can
			either be a dictionary with the frame info in, or None if the request failed
		"""

		if not self.connected:
			self.logger.critical('__getStatus: OTEStamper board not connected, rejected')
			return

		if channel != FRAME_INTERRUPT_GPIO:
			return

		theres_more = True
		while theres_more:
			frame_info = { 'system_time': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') }

			(success, data) = self.__sendCmd(CMD_FRAME_TIMING_INFO)
			if success:
				(queueSize, leapSeconds, clockStatus, frameSequence, lastPPSTicks, frameTicks, unixEpoch) = struct.unpack('=BbBBIII', data)

				if self.lastFrameSequence is not None and frameSequence == self.lastFrameSequence:
					self.logger.warning('duplicate frame sequence received: %d, ignored' % frameSequence)
					self.__sendCmd(CMD_CONFIRM_FRAME_RECEIVED)
					continue

				if queueSize == 0:
					self.logger.critical('received interrupt, but no frame in queue')
				else:
					# Calculate the difference in 1/F_CPU between the the GPS PPS clock and the system(OTE) clock
					# Positive numbers mean the system clock is running faster than the GPS
					# Negative numbers mean the system clock is running slower than the GPS
					captureClockSystemDrift = lastPPSTicks - 8000000                # 8000000 = F_CPU
					captureClockSystemDrift = (captureClockSystemDrift * 125) / 1000.0
	
					framePartialSeconds = float(frameTicks) / float(lastPPSTicks)
		
					#self.logger.debug('framePartialSeconds: %0.9f' % framePartialSeconds)
		
					# Adjust by XVS_END_FRAME_OFFSET_NS, amend framePartialSeconds and unixEpoch if we overflowed to the next second
					framePartialSeconds += ProcessOteStamper.XVS_END_FRAME_OFFSET_NS / 1000000000.0
					if framePartialSeconds > 1.0:
						framePartialSeconds -= 1.0
						unixEpoch += 1
		
					frameEndDateTime = datetime.fromtimestamp(unixEpoch)
					frameEndDateTime += timedelta(microseconds=int(framePartialSeconds * 1000000))
		
					nanoseconds_since_2010 = (unixEpoch - 1262304000) * 1000000000
					nanoseconds_since_2010 += int(framePartialSeconds * 1000000000)
		
					frame_info['queueSize']				= queueSize
					frame_info['leapSeconds']			= leapSeconds
					frame_info['clockStatus']			= clockStatus
					frame_info['frameEndDateTime']			= frameEndDateTime
					frame_info['frameEndNanoSecondsSince2010']	= nanoseconds_since_2010	# This is what we use for timestamping
					frame_info['frameSequence']			= frameSequence
					frame_info['captureClockSystemDrift']		= captureClockSystemDrift
					frame_info['frameDuration']			= nanoseconds_since_2010 - self.last_nanoseconds_since_2010
					frame_info['lastPPSTicks']			= lastPPSTicks
					frame_info['framePartialSeconds']		= framePartialSeconds

					frame_info['errorSequence']			= 0
					frame_info['errorCaptureClockSystemDrift']	= 0
					frame_info['errorEndDateTime']			= 0
					frame_info['errorClockStatus']			= 0

					
					# Sanity Checks

					if self.lastFrameSequence is not None:
						sequenceDelta = frame_info['frameSequence'] - self.lastFrameSequence
						if sequenceDelta < 0:
							sequenceDelta += 256
						if sequenceDelta != 1:
							self.logger.critical('bad sequence: %d -> %d' % (self.lastFrameSequence, frame_info['frameSequence']))
							frame_info['errorSequence'] = 1

					if frame_info['captureClockSystemDrift'] < -2000.0 or frame_info['captureClockSystemDrift'] > 2000.0:
						self.logger.critical('bad capture clock system drift: %0.3f' % (frame_info['captureClockSystemDrift']))
						frame_info['errorCaptureClockSystemDrift'] = 1

					if self.lastFrameEndDateTime is not None and frame_info['frameEndDateTime'] <= self.lastFrameEndDateTime:
						self.logger.critical('bad frameEndDatetime: %s is before %s' % (str(frame_info['frameEndDateTime']), str(self.lastFrameEndDateTime)))
						frame_info['errorEndDateTime'] = 1

					if frame_info['clockStatus'] != 0x07 and frame_info['clockStatus'] != 0x0B:
						self.logger.warning('bad clockStatus != 0x07 or 0x0B: 0x%02X' % (frame_info['clockStatus']))
						frame_info['errorClockStatus'] = 1
	
					self.logger.debug('XVS frame end signal: %s system received it: %s' % (frame_info['frameEndDateTime'].strftime('%Y-%m-%dT%H:%M:%S.%f'), frame_info['system_time']))
					#self.logger.debug('XVS frame info: %s' % (frame_info))
		
					self.queue_frameInfo.put(frame_info)

					# Store "last" things for comparison next time
					self.last_nanoseconds_since_2010		= nanoseconds_since_2010
					self.lastFrameSequence				= frameSequence
					self.lastFrameEndDateTime			= frame_info['frameEndDateTime']

					# Confirm frame has been received
					self.__sendCmd(CMD_CONFIRM_FRAME_RECEIVED)

				if queueSize <= 1:
					theres_more = False
			else:
				self.queue_frameInfo.put(None)
				self.logger.critical('received interrupt, but failed to receive frame info from the OTEStamper Board')


	def __getGpsInfo(self):
		"""
			Gets the current gps and status information from the OTEStamper Board and puts "status" on the queue_gpsInfo Queue
			Status can either be a dictionary with status information in, or None if the request failed
		"""

		if not self.connected:
			self.logger.critical('__getGPSInfo: OTEStamper board not connected, rejected')
			return

		(success, data) = self.__sendCmd(CMD_GPS_INFO, log = False)
		if success:
			(latitude, longitude, altitude, numSatellites, fix, pdop, hdop, vdop, unixEpoch, leapSeconds, clockStatus, voltage)  = struct.unpack('=iiiBBHHHIbBH', data)

			latitude	/= 10000000.0
			longitude	/= 10000000.0
			altitude	/= 10.0
			pdop		/= 100.0
			hdop		/= 100.0
			vdop		/= 100.0
			voltage		= (voltage * 3.3) / (1023.0 * 0.1754385)

			if self.fuzz_gps:
				(latitude, longitude, altitude) = self.fuzzGps(latitude, longitude, altitude)

			status = {	'latitude': latitude,
					'longitude': longitude,
					'altitude': altitude,
					'numSatellites': numSatellites,
					'fix': fix,
					'pdop': pdop,
					'hdop': hdop,
					'vdop': vdop,
					'leapSeconds': leapSeconds,
					'clockStatus': clockStatus,
					'unixEpoch': unixEpoch,
					'voltage': voltage }

			self.__queue_clear(self.queue_gpsInfo)
			self.queue_gpsInfo.put(status)
		else:
			self.logger.critical('failed to receive status from the OTEStamper board')
			self.queue_gpsInfo.put(None)


	def __queue_clear(self, q):
		try:
			while True:
				q.get_nowait()
		except queue.Empty:
			pass


	def main(self, queue_logger, queue_frameInfo, queue_gpsInfo, queue_cmd):
		"""
			main execution loop for this process.  Sets up GPIO inetrrupts, makes sure there's an OTEStamper
			board present and then listens for commands and frame interrupts, sending information acquired
			from the boards into the queues provided as parameters.
		"""

		self.logger = ProcessLogger.startChildLogging(queue_logger, name = 'otestamper')

		# Setup to receive interrupt signals from FRAME_INTERRUPT_GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(FRAME_INTERRUPT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

		self.last_nanoseconds_since_2010 = 0

		# Store the queues we need to read/write to
		self.queue_frameInfo	= queue_frameInfo
		self.queue_gpsInfo	= queue_gpsInfo
		self.queue_cmd		= queue_cmd

		self.fuzz_gps = False

		# Open up the SPI connection to OTEStamper
		ospi.open(0, 0, OSPI_SPEED_HZ, OSPI_START_DELAY)

		# Query OTEStamper to determine the version of if we have a board there
		self.connected = False
		#(success1, data) = self.__sendCmd(CMD_COLD_RESTART_GPS)
		(success1, dataMagic) = self.__sendCmd(CMD_ID_MAGIC_NUMBER)
		(success2, dataFirmware) = self.__sendCmd(CMD_FIRMWARE_VERSION)
		if success1 and success2:
			(otestamperId,)  = struct.unpack('=I', dataMagic)
			(firmwareVersion,)  = struct.unpack('=H', dataFirmware)
			if otestamperId == ProcessOteStamper.OTESTAMPER_ID:
				self.logger.info('---- OTEStamper Board Found ----')
				self.logger.info('    Magic:            0x%X' % otestamperId)
				self.logger.info('    Firmware Version: %d' % firmwareVersion)
				self.connected = True
			else:
				raise ValueError('Unable to locate the OTEStamper Board, magic id does not match')
		else:
			raise ValueError('Failed to contact the OTEStamper Board')

		#(success, data) = self.__sendCmd(CMD_TIMING_TEST_ON)
		(success, data) = self.__sendCmd(CMD_TIMING_TEST_OFF)

		# Setup signal handler so that process signals (e.g. CTRL-C) can kill the process
		signal.signal(signal.SIGINT, self.__cleanup_handler)
		signal.signal(signal.SIGTERM, self.__cleanup_handler)

		# Loop waiting and processing commands
		# Note: The Frame Interrupts are automatic in a seperate thread
		while True:
			cmd = self.queue_cmd.get()
		
			if   cmd == 'gpsinfo':
				self.__getGpsInfo()

			elif cmd == 'startRecording':
				self.logger.info('command Received: %s' % cmd)
				self.last_nanoseconds_since_2010 = 0
				self.lastFrameSequence = None
				self.lastFrameEndDateTime = None
				self.__queue_clear(self.queue_frameInfo)
				GPIO.add_event_detect(FRAME_INTERRUPT_GPIO, GPIO.RISING, self.__frameInterrupt)
				self.__sendCmd(CMD_FRAME_TIMING_INFO_INTERRUPT_ON)
				self.recording = True

			elif cmd == 'stopRecording':
				self.logger.info('command Received: %s' % cmd)
				GPIO.remove_event_detect(FRAME_INTERRUPT_GPIO)
				self.__sendCmd(CMD_FRAME_TIMING_INFO_INTERRUPT_OFF)
				self.__queue_clear(self.queue_frameInfo)
				self.recording = False

			elif cmd == 'led on':
				self.__sendCmd(CMD_LED_ON)

			elif cmd == 'led off':
				self.__sendCmd(CMD_LED_OFF)

			elif cmd == 'fan on':
				self.__sendCmd(CMD_FAN_ON)

			elif cmd == 'fan off':
				self.__sendCmd(CMD_FAN_OFF)

			elif cmd == 'buzzer on':
				self.__sendCmd(CMD_BUZZER_ON)

			elif cmd == 'buzzer off':
				self.__sendCmd(CMD_BUZZER_OFF)

			elif cmd == 'coldrestartgps':
				self.__sendCmd(CMD_COLD_RESTART_GPS)

			elif cmd == 'timingtest on':
				self.__sendCmd(CMD_TIMING_TEST_ON)

			elif cmd == 'timingtest off':
				self.__sendCmd(CMD_TIMING_TEST_OFF)

			elif cmd == 'fuzz gps':
				self.fuzzGpsSetup()

			elif cmd == 'terminate':
				self.logger.info('command Received: %s' % cmd)
				self.logger.info('terminating ProcessOTEStamper')
				break

			else:
				self.logger.info('command Received: %s' % cmd)
				raise ValueError('Unrecognized command: %s' % (cmd))

		# Exit and cleanup
		self.__cleanup_handler(None, None)


	def fuzzGpsSetup(self):
		# If fuzzing is enabled, setup the amount we're fuzzing by
		self.fuzz_gps = True
		self.fuzz_lat = ((random.random() * 2) - 1.0) * 5.0
		self.fuzz_lon = ((random.random() * 2) - 1.0) * 5.0
		self.fuzz_alt = ((random.random() * 2) - 1.0) * 500.0


	def fuzzGps(self, lat, lon, alt):
		# Fuzz the gps if enabled
		lat		= lat + self.fuzz_lat 
		lon		= lon + self.fuzz_lon
		alt		= alt + self.fuzz_alt 

		if lat <= -90:
			lat += 5.0
		if lat >= 90:
			lat -= 5.0

		if lon <= -180:
			lon += 5.0
		if lon >= 180:
			lon -= 5.0

		if alt < 0:
			alt += 500.0

		return (lat, lon, alt)
