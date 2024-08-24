# TODO

* David: "That's fine for the long events we used to record, with durations of 3s or more, but for shorter occultations, I agree with Bob Anderson, always record at least 30s before and after. The 10x rule is only for the highest chance of detecting satellites, but for MB objects, satellites out to 100x are possible, but in practice, they are rarely found more than 10x away."
* Double chord spacing and kml
* Vizier light curve submission
* https://datasheets.raspberrypi.com/camera/raspberry-pi-camera-guide.pdf - INFO for libcamera future upgrade
* 
* Allow magnitude to be selected whilst in exposure analysis
* Any chance you could allow a dynamic (local) change of the limiting magnitude during Exposure Analysis, rather than forcing us to stop and restart Astrid to get to the settings for Simulator? - Ted
* Magnitudes Cluttered on Display Analysis
* Significant red errors when recording with Software Leap Seconds
* Add YYYYMMDD_ to folder name (check that's correct on IOTA Report format
* Repeat prepoint when failed 
* Mention heat sinks in the kit
* Astrid saves fits files as .fit, change to fits (maybe)
* GPS Antenna must be attached when recording video, no GPS popup msg or prevent recording as it currently hangs
* Add mag drop calculator to Astrid
* Multiple deletes on events
* Generate KMZ for multi station videos
* Order occultations by the next one first, can more be automated?  Can frame rate be pre entered?
* Quotes in Wifi names = bad Ted's Wifi, update doc
* astropy download
* For Occultation Info Screen, calc Error In Time, Shadow Width, Path Uncertainty in km's
* Any value to updating duration of event via path computation?
* Experiment with AELocked (looks like a converence thing)
* Check into FITs, is it really storing 0-255 or 0-1023?
Metadata: {'SensorTimestamp': 22567493602000, 'ScalerCrop': (3, 0, 1450, 1088), 'DigitalGain': 1.0002992153167725, 'SensorBlackLevels': (3840, 3840, 3840, 3840), 'AeLocked': False, 'Lux': 400.0, 'FrameDuration': 200014, 'AnalogueGain': 1.0, 'ExposureTime': 199940}
* Frame rates: At speeds above 25fps, one of the python processes pegs out at close to 95-100% cpu on "top".  Figure out cause to increase frame rate.  Also, look at modding picamera to be able to skip frames that are more than 10fps for display.  Accelerated Rendering is likely faster and won't drop frames?   * See /usr/lib/python3/dist-packages/picamera2/previews/q_picamera2.py for display rendering
* Confusion over Object Panel.  Maybe change Object to Target.  But what happens if I say "no".  Is this object now selected as the object to use with Plate Solve comparisons?  How do I know what object is currently the "target"
* Install PyMovie/PyOTE on the Pi

* Complete:
	* Focus Support
	* Histogram 
* Bug: Test this again: If framewriter process raises an exception, it isn't logged, force the raising of exceptions on framewriter, processotestamper and processlogger both during recording video and in regular operation
* Manual reset of OTEStamper
* Make mount panel user configurable for J2000 or JNOW (Steve)
* Update image in response to check boxes without requiring image to be retaken
* Refactor "evolved" CameraModel.py into a command based system and decouple everything so everything runs as a command, updating the UI as appropriate.  This will also get ready for command based operation/scripting. (similar approach to Siril)
* Change to Indi Neutral https://www.indilib.org/api/classINDI_1_1Telescope.html
* Put target on screen to show the star.
* http://www.lunar-occultations.com/occult4/gaia16_edr3.zip
* Use astrometry.net to annotate image and place marker for target on. Add star locations for target confirmation. Too slow to generate images: try using sirils catalogues to annotate or the catalogues above
* Ability to display ravf and fits on pi

* PyMovie:
	* pip3 install adv2
	* pip2 install --no-deps "git+https://github.com/ChasinSpin/pymovie.git"
	* Fails due to adv2 library not being compiled for raspberry pi


# Notes

* NEO's are typically 1/10s occultation (100fps)
* Trans Neptunians = 1 to 0.5fps


## Raspberry Pi GPIO

* raspi-gpio get		# Displays current configuration of the pins
* raspi-gpio funcs	# Displays what all the pins are capable of
* pinout				# Displays Raspberry Pi Pinout

## Links - GPS

* [GPS Raspberry Pi Setup](https://www.youtube.com/watch?v=YfgX7qPeiqQ)
* [GPS Raspberry Pi Setup - Chrony](https://n4bfr.com/2020/04/raspberry-pi-with-chrony/2/)
* [GT-U7](https://x2robotics.ca/gt-u7-gps-module-compatible-neo-6m-stm32-with-eeprom-antenna-for-arduino)
* [Getting GPS to work on your Pi](https://area-51.blog/2012/06/18/getting-gps-to-work-on-a-raspberry-pi/)
* [GPSd accuracy](https://gpsd.gitlab.io/gpsd/gpsd-time-service-howto.html)
* [PPS-Client v1.5.2](https://github.com/rascol/Raspberry-Pi-PPS-Client)
* [GT-U7 Chip Datasheet](https://images-na.ssl-images-amazon.com/images/I/91tuvtrO2jL.pdf)
* [GPS Dimensions](https://www.aliexpress.com/item/32828958211.html)

# Links - General

* [Astro Digital Video](http://www.hristopavlov.net/adv/index.html)
* [AstroDigitalVideo GitHub](https://github.com/AstroDigitalVideo)
* [Bob Anderson GitHub](https://github.com/bob-anderson-ok)
* [PiJuice](https://github.com/PiSupply/PiJuice)
* [PS Series 3V Buzzer](https://www.jp.tdk.com/tefe02/ef532_ps.pdf)
* [QHY174GPS Design and Timing](https://www.qhyccd.com/wp-content/uploads/20210628792.pdf)
* [Raspberry Pi 4 Pinout](https://linuxhint.com/gpio-pinout-raspberry-pi/)

# Github Branches

* List Branches: git branch# asterisk branch is the active one
* git pull
* git push
* New Branch: On Github, click branches and New Branch 
* Update local github: git pull   
* Checkout Branch: git checkout mybranch
* Commit as normal
* Switching back to main branch:  git checkout main
* Merging:  git checkout main;  git merge mybranch; git push    # then:
* Delete mybranch:  On Github, click branches and Delete the Branch 
* git pull

# Accelerated Graphics

Currently, camera doesn't work when doing accelerated graphics, try out V4L2 instead: [https://www.arducam.com/faq/opencv-v4l2-python-rpi/](https://www.arducam.com/faq/opencv-v4l2-python-rpi/)

Enable Acceleration:

	pi@astrid5:/boot $ diff config.txt config.txt~
	62,63c62
	< #dtoverlay=vc4-kms-v3d
	< dtoverlay=vc4-fkms-v3d-pi4
	---
	> dtoverlay=vc4-kms-v3d
	89,95d87
	< hdmi_force_hotplug=1
	< #hdmi_ignore_edid=0xa5000080
	< hdmi_group=2
	< hdmi_mode=23
	< #framebuffer_width=1280
	< #framebuffer_height=720
	< #gpu_mem=256
	
	root@astrid5:~/.vnc/config.d# pwd
	/root/.vnc/config.d
	root@astrid5:~/.vnc/config.d# diff vncserver-x11 vncserver-x11~
	4,6d3
	< CaptureTech=raspi
	< ExperimentalRaspiCapture=1
	< ServerPreferredEncoding=JPEG
	
	pi@astrid5:~/astrid/app $ git diff
	diff --git a/app/CameraModel.py b/app/CameraModel.py
	index 4d528a0..cedf6e5 100644
	--- a/app/CameraModel.py
	+++ b/app/CameraModel.py
	@@ -242,7 +242,8 @@ class CameraModel:
                vflip     = self.settings['vflip']
                transform = Transform(hflip=hflip, vflip=vflip)
 
	-               if self.settings['accelerated_preview']:
	+               #if self.settings['accelerated_preview']:
	+               if True:
                        print("Configuring Accelerated Preview")
                        self.qt_picamera = QGlPicamera2(self.picam2, width=self.previewWidth, height=self.previewHeight, keep_ar=True, transform=transform)
                else:

	
	sudo reboot
	
	
# Next Gen Camera

	pi@astrid5:~ $ libcamera-vid --list-cameras
	Available cameras
	-----------------
	0 : imx296 [1456x1088] (/base/soc/i2c0mux/i2c@1/imx296@1a)
   		 Modes: 'R10_CSI2P' : 728x544 [117.61 fps - (0, 0)/1456x1088 crop]
                		      1456x1088 [60.38 fps - (0, 0)/1456x1088 crop]

[https://www.waveshare.com/wiki/Template:RPi_Camera_Libcamera_Guide](https://www.waveshare.com/wiki/Template:RPi_Camera_Libcamera_Guide)

	libcamera-vid -t 10000 --framerate 117.61 -o test.h264
	ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 test.h264 
	1167   (number of frames)
	
[https://forum.arducam.com/t/64mp-what-is-the-quickest-way-to-grab-an-image-in-python/3486](https://forum.arducam.com/t/64mp-what-is-the-quickest-way-to-grab-an-image-in-python/3486)

[https://pypi.org/project/rpi-libcamera/#description](https://pypi.org/project/rpi-libcamera/#description)

[https://libcamera.org/docs.html](https://libcamera.org/docs.html)

[https://github.com/raspberrypi/picamera2/blob/main/picamera2/picamera2.py](https://github.com/raspberrypi/picamera2/blob/main/picamera2/picamera2.py)
