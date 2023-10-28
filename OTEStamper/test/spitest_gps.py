#!/usr/bin/env python3

import ospi
import time
import struct

CMD_ID_MAGIC_NUMBER			= 0x70
CMD_FIRMWARE_VERSION			= 0x71
CMD_LED_ON				= 0x72
CMD_LED_OFF				= 0x73
CMD_FAN_ON				= 0x74
CMD_FAN_OFF				= 0x75
CMD_TIMING_TEST_ON			= 0x76
CMD_TIMING_TEST_OFF			= 0x77
CMD_COLD_RESTART_GPS			= 0x78
CMD_FRAME_TIMING_INFO_INTERRUPT_ON	= 0x79
CMD_FRAME_TIMING_INFO_INTERRUPT_OFF	= 0x7A
CMD_BUZZER_ON				= 0x7B
CMD_BUZZER_OFF				= 0x7C
CMD_GPS_INFO				= 0x90
CMD_FRAME_TIMING_INFO			= 0x91
CMD_CONFIRM_FRAME_RECEIVED		= 0x92
CMD_TEST_FRAME_FOR_VALIDATION		= 0x93

def bytesToHexStr(b):
	str = ' '.join('0x{:02x}'.format(x) for x in b)
	return str


ospi.open(0, 0, 2000000, 15)
first = True

while True:
	(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(CMD_GPS_INFO, 0x1C, 4)
	
	if success == 0:
		print('failed: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
	elif retries != 0:
		print('retried: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
	else:
		#print('success: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
		(latitude, longitude, altitude, numSatellites, fix, pdop, hdop, vdop, unixEpoch, leapSeconds, clockStatus, voltage)  = struct.unpack('=iiiBBHHHIbBH', data)

		latitude	/= 10000000.0
		longitude	/= 10000000.0
		altitude	/= 10.0
		pdop		/= 100.0
		hdop		/= 100.0
		vdop		/= 100.0
		voltage		=  (voltage * 3.3) / (1023.0 * 0.1754385)

		gps = {	'latitude': latitude,
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

		print(gps)

	time.sleep(0.5)

ospi.close()
