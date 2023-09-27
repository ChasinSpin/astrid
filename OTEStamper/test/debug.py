#!/usr/bin/env python3

import time
import serial

port = '/dev/ttyAMA1'
baud = 9600

print("Listening to uart5 rx (Gpio 13)...")
ser = serial.Serial(port=port,
		    baudrate=baud,
		    parity=serial.PARITY_NONE,
		    stopbits=serial.STOPBITS_ONE,
		    bytesize=serial.EIGHTBITS,
		    timeout=1)

while 1:
	x = ser.read()
	if len(x) > 0:
		print("%c" % x[0], end='')
