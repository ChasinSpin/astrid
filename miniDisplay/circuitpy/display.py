import time
import json
import board
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from displayio import Group



class Display():

	LINES_Y	= [20, 50, 80, 110]

	
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


	def updateDisplayButtonPressed(self):
		group = Group()
		group.append(self.__makeTextArea('SWITCHING NETWORK', 0x666666, 0, self.LINES_Y[0]))
		group.append(self.__makeTextArea('MODES, PLEASE WAIT', 0x666666, 0, self.LINES_Y[1]))
		group.append(self.__makeTextArea('FOR COMPLETION...', 0x666666, 0, self.LINES_Y[2]))
		self.systemDisplay.root_group = group


	def updateDisplayJson(self, jstr):
		status = json.loads(jstr)

		group = Group()

		if   status['version'].split('.')[0:2] != self.version.split('.')[0:2]:
			group.append(self.__makeTextArea('VERSION MISMATCH !', 0xFF0000, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('%s != %s' % (status['version'], self.version), 0xFF0000, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Run Install Mini Display', 0xFF0000, 0, self.LINES_Y[2]))
			group.append(self.__makeTextArea('in Astrid Tools', 0xFF0000, 0, self.LINES_Y[3]))
		elif status['network']['mode'] == 'wifi hotspot':
			group.append(self.__makeTextArea('WIFI: %s' % status['network']['ssid'], 0xFFFF00, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
		elif status['network']['mode'] == 'wifi managed':
			group.append(self.__makeTextArea('WIFI: %s' % status['network']['ssid'], 0x00FF00, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
			group.append(self.__makeTextArea('Freq: %sGHz  Signal: %s' % (status['network']['frequency'], status['network']['linkquality']), 0x00FFFF, 0, self.LINES_Y[3]))
		elif status['network']['mode'] == 'ethernet':
			group.append(self.__makeTextArea('ETHERNET', 0x00FF00, 0, self.LINES_Y[0]))
			group.append(self.__makeTextArea('IP: %s' % status['network']['ip'], 0x00FFFF, 0, self.LINES_Y[1]))
			group.append(self.__makeTextArea('Host: %s' % status['network']['hostname'], 0x00FFFF, 0, self.LINES_Y[2]))
		else:
			group.append(self.__makeTextArea('UNKNOWN: %s' % status['network']['mode'], 0x00FF00, 0, self.LINES_Y[0]))

		self.systemDisplay.root_group = group
