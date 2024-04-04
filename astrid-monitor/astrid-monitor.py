#!/usr/bin/env python3

import json
import psutil
import socket
import subprocess
import time
import serial
import adafruit_board_toolkit.circuitpython_serial
from datetime import datetime


version = '1.0.0'

minidisplay_present	= True
MONITOR_REPEAT		= 5		# Seconds



def runCommand(cmd, line_starts_with = None):
	"""
		Runs a command, cmd is an array consisting of the command and parameters
		If line_starts_with is set to a str, the first line with starting with that string is returned,
		otherwise returns stdout from the command
	"""
	result = subprocess.run(cmd, capture_output = True, text = True)
	if line_starts_with is not None:
		lines = result.stdout.split('\n')
		for line in lines:
			if line.startswith(line_starts_with):
				return line
	return result.stdout


def extractIP4Address(snicaddrs):
	# Extracts the IP4 Address out of psutil net_if_addrs
	for snicaddr in snicaddrs:
		if snicaddr.family == socket.AF_INET:
			return snicaddr.address
	return None
	

def getNetworkStatus():
	""" Gets the network configuration and returns it as a dictionary """
	status = {}

	# Obtain IP addresses (only works with IP4 currently)
	wlan0_ip = None
	eth0_ip = None
	if_addrs = psutil.net_if_addrs()
	if 'wlan0' in if_addrs.keys():
		wlan0_ip = extractIP4Address(if_addrs['wlan0'])
	if 'eth0' in if_addrs.keys():
		eth0_ip = extractIP4Address(if_addrs['eth0'])

	hostname = socket.gethostname() + '.local'
	#print('hostname:', hostname)

	if eth0_ip is None:
		iwconfig_result = runCommand( ['/usr/sbin/iwconfig', 'wlan0'] )

		essid = None
		freq = None
		link_quality = None
		ip_addr = wlan0_ip

		# Scan the iwconfig output and parse what we need
		for line in iwconfig_result.split('\n'):
			if 'ESSID:"' in line:
				essid = line.split('ESSID:"')
				essid = essid[1].split('" ')[0]
			if 'Mode:' in line:
				mode = (line.split('Mode:')[1]).split(' ')[0]
			if 'Frequency:' in line:
				freq = (line.split('Frequency:')[1]).split(' ')[0]
			if 'Link Quality=' in line:
				link_quality = (line.split('Link Quality=')[1]).split(' ')[0]

		# If we're running Ad-hoc, then get the ESSID from the hostapd.conf file
		if mode == 'Master':
			with open('/etc/hostapd/hostapd.conf') as fp:
				lines = [line.rstrip() for line in fp]
			for line in lines:
				if line.startswith('ssid='):
					essid = line.split('ssid=')[1]
					break
			
		#print('ESSID:<%s>' % essid)
		#print('mode:<%s>' % mode)
		#print('freq:<%s>' % freq)
		#print('link_quality:<%s>' % link_quality)
	
		if mode == 'Managed':
			status['mode'] = 'wifi managed'
			status['ssid'] = essid
			status['ip'] = ip_addr
			status['hostname'] = hostname
			status['frequency'] = freq
			status['linkquality'] = link_quality
		elif mode == 'Master':
			status['mode'] = 'wifi hotspot'
			status['ssid'] = essid
			status['ip'] = ip_addr
			status['hostname'] = hostname
		else:
			status['mode'] = 'unknown'
	else:
		status['mode'] = 'ethernet'
		ip_addr = eth0_ip
		status['ip'] = ip_addr
		status['hostname'] = hostname

	return status


def getAstridStatus():
	""" Gets the astrid status and returns it as a dictionary """
	status = {}
	return status


def getStatus():
	""" Get the status of the system and returns it as a dictionary """
	now = datetime.now()

	status = {}
	status['version']	= version
	status['timestamp']	= now.strftime('%Y-%m-%d %H:%M:%S UTC')
	status['network']	= getNetworkStatus()
	status['astrid']	= getAstridStatus()
	return status


#
# MAIN
#

serialPort = None

while True:
	status = getStatus()

	comports = adafruit_board_toolkit.circuitpython_serial.repl_comports()
	if comports:
		if serialPort is None:
			# If we have a mini display connected, write to it
			serial_device = comports[0].device
			serialPort = serial.Serial(port = serial_device, baudrate = 115200, bytesize = 8, timeout = MONITOR_REPEAT, stopbits = serial.STOPBITS_ONE)
	else:
		if serialPort is not None:
			serialPort.close()
		serialPort = None
		#print(status)

	d0Pressed = False
	d1Pressed = False
	d2Pressed = False

	if serialPort is not None:
		jstr = 'ASTRIDMONITOR:' + json.dumps(status, indent=4) + '\r'
		serialPort.write(bytes(jstr, 'ascii'))
		#print(jstr)

		# Read button presses
		try:
			lines = serialPort.readlines()
		except:
			pass

		for line in lines:
			if line == b'MINIDISPLAY:ButtonD0\r\n':
				d0Pressed = True
			if line == b'MINIDISPLAY:ButtonD1\r\n':
				d1Pressed = True
			if line == b'MINIDISPLAY:ButtonD2\r\n':
				d2Pressed = True
	else:
		time.sleep(MONITOR_REPEAT)

	if d0Pressed:
		print('Button D0 Pressed')
	if d1Pressed:
		print('Button D1 Pressed')
	if d2Pressed:
		print('Button D2 Pressed')
