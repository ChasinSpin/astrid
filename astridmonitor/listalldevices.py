#!/usr/bin/env python3

import serial.tools.list_ports

print("All devices:")

ports = serial.tools.list_ports.comports()
for port in ports:
	print(port.interface)
	print(port.name)
	print(port.device)
