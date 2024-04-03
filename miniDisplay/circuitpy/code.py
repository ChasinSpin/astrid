import time
import board
import digitalio
import supervisor
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_debouncer import Debouncer
from display import Display



PREFIX		='ASTRIDMONITOR:'
MONITOR_TIMEOUT	= 12			# Seconds

d0Pin = digitalio.DigitalInOut(board.D0)
d1Pin = digitalio.DigitalInOut(board.D1)
d2Pin = digitalio.DigitalInOut(board.D2)

d0Pin.pull = digitalio.Pull.UP

d0Button = Debouncer(d0Pin)
d1Button = Debouncer(d1Pin)
d2Button = Debouncer(d2Pin)

with open('/version.txt') as fp:
	version = fp.readline()
version = version.rstrip()
#print('Version:<%s>' % version)

display = Display(version)
lastUpdate = None

while True:
	d0Button.update()
	d1Button.update()
	d2Button.update()

	now = time.time()

	if d0Button.fell:
		print('MINIDISPLAY:ButtonD0')
	if d1Button.rose:
		print('MINIDISPLAY:ButtonD1')
	if d2Button.rose:
		print('MINIDISPLAY:ButtonD2')

	if lastUpdate is not None and (lastUpdate + MONITOR_TIMEOUT) < now:
		timed_out = True
	else:
		timed_out = False
	
	count = supervisor.runtime.serial_bytes_available

	if count > 0:
		jstr = input()

		if jstr.startswith(PREFIX):
			lastUpdate = now
			jstr = jstr.replace(PREFIX, '')
			display.updateDisplayJson(jstr)
			#print(jstr)

	if timed_out:
		display.updateDisplayTimedOut()
		time.sleep(1)
