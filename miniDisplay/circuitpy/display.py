import time
import json
import board
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from displayio import Group



class Display():

	LINES_Y	= [20, 50, 80, 110]

	status = {}

	
	def __init__(self, version):
		self.systemDisplay = board.DISPLAY
		self.font = bitmap_font.load_font("fonts/Helvetica-Bold-16.bdf")

		group = Group()

		group.append(self.__makeTextArea('Astrid Mini Display', 0xFF00FF, 0, self.LINES_Y[0]))
		group.append(self.__makeTextArea('Version: %s' % version, 0xFF00FF, 0, self.LINES_Y[2]))
		group.append(self.__makeTextArea('Author: @ChasinSpin', 0xFF00FF, 0, self.LINES_Y[3]))
		self.systemDisplay.root_group = group

		time.sleep(2)

		group = Group()
		group.append(self.__makeTextArea('Waiting for data...', 0xFF00FF, 0, self.LINES_Y[0]))
		self.systemDisplay.root_group = group

		self.version	= version


	def __makeTextArea(self, text, color, x, y):
		text_area = label.Label(self.font, text=text, color=color)
		text_area.x = x
		text_area.y = y
		return text_area


	def updateDisplayTimedOut(self):
		group = Group()
		group.append(self.__makeTextArea('ASTRID MONITOR', 0xFF0000, 0, self.LINES_Y[0]))
		group.append(self.__makeTextArea('NOT RUNNING !', 0xFF0000, 0, self.LINES_Y[1]))
		self.systemDisplay.root_group = group


	def updateDisplayButtonPressed_D0_D1(self):
		group = Group()
		if self.status['shutdown']['shutdownMode'] > 0:
			group.append(self.__makeTextArea('Please wait, cancelling', 0x666666, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('poweroff!', 0x666666, 0, self.LINES_Y[1]))
		else:
			group.append(self.__makeTextArea('SWITCHING NETWORK', 0x666666, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('MODES, PLEASE WAIT', 0x666666, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('FOR COMPLETION...', 0x666666, 0, self.LINES_Y[2]))
			group.append(self.__makeTextArea('_< This button for poweroff...', 0xFF0000, 0, self.LINES_Y[3]))
		self.systemDisplay.root_group = group


	def updateDisplayButtonPressed_D2(self):
		group = Group()
		group.append(self.__makeTextArea('Detected poweroff button', 0x666666, 0, self.LINES_Y[0]))
		group.append(self.__makeTextArea('press, sending to Astrid,', 0x666666, 0, self.LINES_Y[1]))
		group.append(self.__makeTextArea('please wait!', 0x666666, 0, self.LINES_Y[2]))
		self.systemDisplay.root_group = group
		self.systemDisplay.root_group = group


	def updateDisplayJson(self, jstr):
		self.status = json.loads(jstr)

		group = Group()

		if   self.status['version'].split('.')[0:2] != self.version.split('.')[0:2]:
			group.append(self.__makeTextArea('VERSION MISMATCH !', 0xFF0000, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('%s != %s' % (self.status['version'], self.version), 0xFF0000, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Run Install Mini Display', 0xFF0000, 0, self.LINES_Y[2]))
			group.append(self.__makeTextArea('in Astrid Tools', 0xFF0000, 0, self.LINES_Y[3]))
		elif self.status['shutdown']['shutdownMode'] > 0:
			if self.status['shutdown']['shutdownMode'] == 1:
				group.append(self.__makeTextArea('Press any other buttons on', 0x666666, 0, self.LINES_Y[0]))
				group.append(self.__makeTextArea('left to cancel', 0x666666, 0, self.LINES_Y[1]))
				group.append(self.__makeTextArea('_< Press again to poweroff...', 0xFF0000, 0, self.LINES_Y[3]))
			elif self.status['shutdown']['shutdownMode'] >= 2:
				group.append(self.__makeTextArea('ASTRID is POWERING', 0xFF0000, 0, self.LINES_Y[0]))
				group.append(self.__makeTextArea('OFF! Wait 15 seconds after', 0xFF0000, 0, self.LINES_Y[1]))
				group.append(self.__makeTextArea('green LED and display go', 0xFF0000, 0, self.LINES_Y[2]))
				group.append(self.__makeTextArea('out before removing power.', 0xFF0000, 0, self.LINES_Y[3]))
		elif self.status['network']['mode'] == 'wifi hotspot':
			group.append(self.__makeTextArea('WIFI: %s' % self.status['network']['ssid'], 0xFFFF00, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % self.status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % self.status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
		elif self.status['network']['mode'] == 'wifi managed':
			sigLevel = self.status['network']['signallevel']

			# Below -67 dBm we don't have enough signal for reliable/fast packet delivery
			ssid = self.status['network']['ssid']
			if sigLevel == '' or ssid == '':
				wifiLineColor = 0x666666
			elif int(sigLevel) >= -67:
				wifiLineColor = 0x00FF00
			else:
				wifiLineColor = 0xFF0000

			# Add dBm to signal level
			if sigLevel != '':
				sigLevel += 'dBm'

			# Add GHz to frequency
			freq = self.status['network']['frequency']
			if freq != '':
				freq += 'GHz'

			group.append(self.__makeTextArea('WIFI: %s  %s' % (self.status['network']['ssid'], sigLevel), wifiLineColor, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % self.status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % self.status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
			group.append(self.__makeTextArea('Freq: %s  LinkQ: %s' % (freq, self.status['network']['linkquality']), 0x00FFFF, 0, self.LINES_Y[3]))
		elif self.status['network']['mode'] == 'ethernet':
			group.append(self.__makeTextArea('ETHERNET', 0x00FF00, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % self.status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % self.status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
		else:
			group.append(self.__makeTextArea('UNKNOWN: %s' % self.status['network']['mode'], 0x00FF00, 0, self.LINES_Y[0]))

		self.systemDisplay.root_group = group
