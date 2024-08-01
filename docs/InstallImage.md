# Install From Astrid Image
	
## Restoring Image

NOTE: These instructions have changed on August 1st 2024
		
Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to restore image (e.g. 2024-08-01-astrid.img.xz).

* Operating System: Choose "Use Custom" and locate 2024-08-01-astrid.img.xz 

* Storage: Choose the SD Card you are writing to **IMPORTANT:** Make sure you have selected the correct SD Card (i.e. don't overwrite other drives by mistake).

* In Settings (Advanced options), uncheck:
	* Set hostname
	* Enable SSH
	* Set username and password
	* Configure wireless LAN
	* Set locale settings
* Click Write and wait for the writing and verification to finish

* Remove SD Card

Insert card into Raspberry Pi and boot - see [Startup in UsageGuide](UsageGuide.md#Startup).  Wait for 5-10mins for card to be resized.  When completed, connect via WiFi from a tablet or PC to:

|           |                |
| --------- | -------------- |
| Wifi SSID | AstridHotspot |
| Wifi Password | iotaiota |
| Hostname | astrid.local (or 10.0.0.5 on windows) |

Note: It can take a few mins for astrid.local to be pushed to the device you are connecting from and may result in Hostname not found.

## Initial Configuration Of Astrid

Connect via VNC using the above connection details.

See the following sections in the [Usage Guide](UsageGuide.md):

* [First Light](UsageGuide.md#first-light)
* [Connect Via VNC](UsageGuide.md#connect-via-vnc)
* [Internet Access Optional](UsageGuide.md#internet-access-optional)

### Change Hostname

If you have multiple Astrids, or someone else has an Astrid near you, confusion about which one you are connecting to can occur, and each Astrid requires a unique network and name.

##### Wifi Hotspot Change	

1. Run WifiSetup on the desktop (under Astrid Tools), and change the access points SSID and password (option 7) to:

		SSID: AstridXHotspot  (where X is a unique number for your astrid)
		Password: iotaiota
	
2.	Then use Option 5 to add your home network.
	
##### Hostname Change

* Raspberry Pi Symbol (top left) / Preferences / Raspberry Pi Configuration
	
* Under System, click on Change Hostname and set to:
		astridX 	(where X is a unique number for your astrid)
		
* Click OK and Reboot

### Upgrade Astrid To Latest

Connect to Astrid using the **NEW** network credentials and hostname:
		
* Run Astrid Upgrade on the desktop
* Reboot when prompted

### Testing Astrid

1. Connect USB Drive

2.	Connect GPS Antenna

3. Run Astrid App and choose Simulator
	
4. Check all Status buttons are Green, if not green, then wait for GPS satellites to be found (can take 20min).
	
5. If GPS/Timing/Acquisition are Green and Site is Red or Yellow, click on Site and Update Site and Mount
	
6. Switch Task to OTE Video and press the record button for 5 seconds, and then press again to stop.  All status buttons should still be green.
If not, click on the button to discover the issue.

### IOTA Build Instructions

* Create SD Card from image using the instructions above and image: 2024-08-01-astrid-ted.img.xz (DO NOT REDISTRIBUTE THIS IMAGE)
* Plug in USB Drive, GPS Antenna and MiniDisplay into Pi
* Insert the card into Raspberry Pi and startup (wait 5-10mins for card to be resized)
* Use MiniDisplay to switch to home network
* Connect via home network to astrid.local
* Start terminal and type: ./astrid/scripts/iotaconfigure.sh  and follow instructions
* After reboot, start astrid and choose Simulator
* Check all status buttons are green, if not wait for GPS satellites to be found (can take 20min in less than ideal conditions)
* Switch task to OTE Video and press record, then 5 seconds later, press stop.  All status buttons should still be green.
* From terminal, type: ~/astrid/scripts/cleanship.sh
* Remove power after 15 seconds
* Ship Astrid