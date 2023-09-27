#!/usr/bin/env python3

import ospi
import time
import struct
from datetime import datetime, timedelta


FPS					= 60.0
TEST_DURATION_SECS			= 60*60

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

XVS_END_FRAME_OFFSET_NS = 59075



def bytesToHexStr(b):
	str = ' '.join('0x{:02x}'.format(x) for x in b)
	return str


ospi.open(0, 0, 2000000, 15)
first = True

lowerFrameDurationLimit = int(((1.0/FPS) * 1000000000.0) * 0.999)
upperFrameDurationLimit = int(((1.0/FPS) * 1000000000.0) * 1.0001)
print('Frame Duration Limits: %d -> %dns' % (lowerFrameDurationLimit, upperFrameDurationLimit))

(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(CMD_FRAME_TIMING_INFO_INTERRUPT_ON, 0x0, 4)
print('Start video camera in ASTRID @ %0.3ffps' % FPS)

last_nanoseconds_since_2010 = 0
lastFrameSequence = None
lastFrameEndDateTime = None
first_frame = True

prev_frame_info = None
printNextFrame = False

histogram_bins_lower = []
histogram_bins_upper = []

histogram_bins_lower.append(0)
histogram_bins_upper.append(lowerFrameDurationLimit-1)

for i in range(lowerFrameDurationLimit, upperFrameDurationLimit, 125):
	histogram_bins_lower.append(i)
	histogram_bins_upper.append(i+125-1)

histogram_bins_lower.append(histogram_bins_upper[-1])
histogram_bins_upper.append(500000000000)

histogram_bins_count = [0] * len(histogram_bins_lower)

start_test_time = datetime.utcnow()
while (datetime.utcnow() - start_test_time).total_seconds() < TEST_DURATION_SECS:
	(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(CMD_FRAME_TIMING_INFO, 0x10, 4)
	
	if success == 0:
		print('failed: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
	elif retries != 0:
		print('retried: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
	else:
		#print('success: %d, data: %s, retries: %d, execution_time_us: %d fail_tx:%d fail_crc:%d' % (success, bytesToHexStr(data), retries, execution_time_us, fail_hardware_tx, fail_crc))
		(queueSize, leapSeconds, clockStatus, frameSequence, lastPPSTicks, frameTicks, unixEpoch)  = struct.unpack('=BbBBIII', data)

		if queueSize >= 1:
			frame_info = {}

			# Calculate the difference in 1/F_CPU between the the GPS PPS clock and the system(OTE) clock
			# Positive numbers mean the system clock is running faster than the GPS
			# Negative numbers mean the system clock is running slower than the GPS
			captureClockSystemDrift = lastPPSTicks - 8000000                # 8000000 = F_CPU
			captureClockSystemDrift = (captureClockSystemDrift * 125) / 1000.0
			#self.logger.debug("captureClockSystemDrift: %0.3fus" % captureClockSystemDrift)

			framePartialSeconds = float(frameTicks) / float(lastPPSTicks)

			#self.logger.debug('framePartialSeconds: %0.9f' % framePartialSeconds)

			# Adjust by XVS_END_FRAME_OFFSET_NS, amend framePartialSeconds and unixEpoch if we overflowed to the next second
			framePartialSeconds += XVS_END_FRAME_OFFSET_NS / 1000000000.0
			if framePartialSeconds > 1.0:
				framePartialSeconds -= 1.0
				unixEpoch += 1

			frameEndDateTime = datetime.fromtimestamp(unixEpoch)
			frameEndDateTime += timedelta(microseconds=int(framePartialSeconds * 1000000))

			nanoseconds_since_2010 = (unixEpoch - 1262304000) * 1000000000
			nanoseconds_since_2010 += int(framePartialSeconds * 1000000000)

			frame_info['queueSize'] = queueSize
			frame_info['leapSeconds'] = leapSeconds
			frame_info['clockStatus'] = clockStatus
			frame_info['frameEndDateTime'] = frameEndDateTime
			frame_info['frameEndNanoSecondsSince2010'] = nanoseconds_since_2010     # This is what we use for timestamping
			frame_info['frameSequence'] = frameSequence
			frame_info['captureClockSystemDrift'] = captureClockSystemDrift
			frame_info['frameDuration'] = nanoseconds_since_2010 - last_nanoseconds_since_2010

			last_nanoseconds_since_2010 = nanoseconds_since_2010

			errorOTE = False

			if lastFrameSequence is not None:
				sequenceDelta = frame_info['frameSequence'] - lastFrameSequence
				if sequenceDelta < 0:
					sequenceDelta += 256
				if sequenceDelta != 1:
					print('**** BAD SEQUENCE: %d -> %d' % (lastFrameSequence, frame_info['frameSequence']))
					errorOTE = True
			lastFrameSequence = frame_info['frameSequence']

			if frame_info['captureClockSystemDrift'] < -100.0 or frame_info['captureClockSystemDrift'] > 100.0:
				print('**** BAD CAPTURE CLOCK SYSTEM DRIFT: %0.3f' % (frame_info['captureClockSystemDrift']))
				errorOTE = True
			
			if not first_frame and (frame_info['frameDuration'] > upperFrameDurationLimit or frame_info['frameDuration'] < lowerFrameDurationLimit):
				print('**** BAD frameDuration: %d' % (frame_info['frameDuration']))
				errorOTE = True
			first_frame = False

			if lastFrameEndDateTime is not None:
				if frame_info['frameEndDateTime'] <= lastFrameEndDateTime:
					print('**** BAD frameEndDatetime: %s is before %s' % (str(frame_info['frameEndDateTime']), str(lastFrameEndDateTime)))
					errorOTE = True
			lastFrameEndDateTime = frame_info['frameEndDateTime']

			if frame_info['queueSize'] != 1:
				print('**** BAD queueSize: %d' % (frame_info['queueSize']))
				errorOTE = True

			#if frame_info['clockStatus'] == 0 or frame_info['clockStatus'] == 255:
			if frame_info['clockStatus'] == 255:
				print('**** CORRECTED timer_overflows = 0: %d' % (frame_info['clockStatus']))
				errorOTE = True

			#if frame_info['clockStatus'] != 0x07:
			#	print('**** BAD clockStatus != 0x00: 0x%02X' % (frame_info['clockStatus']))
			#	errorOTE = True

			if printNextFrame:
				print('Next Frame:', frame_info)
				printNextFrame = False

			if errorOTE:
				print('Previous Frame:', prev_frame_info)
				print('Current Frame:', frame_info)
				printNextFrame = True

			fd = frame_info['frameDuration']
			for i in range(len(histogram_bins_count)):
				if fd >= histogram_bins_lower[i] and fd <= histogram_bins_upper[i]:
					histogram_bins_count[i] += 1
					break

			#print(frame_info)

			prev_frame_info = frame_info

			(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(CMD_CONFIRM_FRAME_RECEIVED, 0x0, 4)

(success, data, retries, execution_time_us, fail_hardware_tx, fail_crc) = ospi.cmd(CMD_FRAME_TIMING_INFO_INTERRUPT_OFF, 0x0, 4)

print('center,lower,upper,count')
for i in range(len(histogram_bins_count)):
	print('%0.1f,%d,%d,%d' % ((histogram_bins_lower[i] + histogram_bins_upper[i]) / 2.0, histogram_bins_lower[i], histogram_bins_upper[i], histogram_bins_count[i]))

ospi.close()
