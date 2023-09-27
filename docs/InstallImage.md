# Install From Astrid Image
	
## Restoring Image
		
Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to restore image (e.g. 2023-08-13-astrid.img.xz).

In Settings (Advanced options), uncheck:

* Set hostname
* Enable SSH
* Set username and password
* Configure wireless LAN
* Set locale settings

Insert card into Raspberry Pi and boot.  Wait for 5-10mins for card to be resized.  When completed, connect to:

|           |                |
| --------- | -------------- |
| Wifi SSID | RPiHotspot |
| Wifi Password | iotaiota |
| Hostname | astrid.local |

Note: It can take a few mins for astrid.local to be pushed to the device you are connecting from and may result in Hostname not found.

## Updates to make since last image

	sudo vi /boot/config.txt
		* comment out: dtoverlay=uart5

	Remove focal length from configs.json on USB key, it now gets loaded from platesolver.json
	
	Rename TestPlateoSolveImages to TestPlateSolveImages on USB Drive
	
	Run WifiSetup on the desktop, and change the access points SSID and password (option 7) to:
		SSID: AstridHotspot
		Password: iotaiota
	
	Then use Option 5 to add your home network.
	
	Raspberry Pi Symbol (top left) / Shutdown Reboot
	
	# Update software to latest
	cd ~/astrid
	git pull
	./install.sh
	sudo reboot
	
	OR
	
	run Astrid Upgrade on the desktop

	
	# Test
	Add USB Drive
	Run Astrid App
