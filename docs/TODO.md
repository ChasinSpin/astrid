# TODO

* New Boards, check buzzer working with new transistor and fan transistor is fully open, max current.
* astropy download
* Steve Calcs
* Countdown to record (Ted)
* Battery Monitor and auto shutdown
* Experiment with AELocked (looks like a converence thing)
* Check into FITs, is it really storing 0-255 or 0-1023?
Metadata: {'SensorTimestamp': 22567493602000, 'ScalerCrop': (3, 0, 1450, 1088), 'DigitalGain': 1.0002992153167725, 'SensorBlackLevels': (3840, 3840, 3840, 3840), 'AeLocked': False, 'Lux': 400.0, 'FrameDuration': 200014, 'AnalogueGain': 1.0, 'ExposureTime': 199940}
* Disable notification about automatic updates from the OS:
https://forums.raspberrypi.com/viewtopic.php?t=331808
* Implement Fan off
* Frame rates: At speeds above 25fps, one of the python processes pegs out at close to 95-100% cpu on "top".  Figure out cause to increase frame rate.  Also, look at modding picamera to be able to skip frames that are more than 10fps for display.  Accelerated Rendering is likely faster and won't drop frames?   * See /usr/lib/python3/dist-packages/picamera2/previews/q_picamera2.py for display rendering
* Taken with Astrid splash screen
* Confusion over Object Panel.  Maybe change Object to Target.  But what happens if I say "no".  Is this object now selected as the object to use with Plate Solve comparisons?  How do I know what object is currently the "target"
* Install PyMovie/PyOTE on the Pi

* Complete:
	* Focus Support
	* Path computation, event time, duration
	* Auto-Stretch lower/upper bound setting
	* Histogram 
* Bug: Test this again: If framewriter process raises an exception, it isn't logged, force the raising of exceptions on framewriter, processotestamper and processlogger both during recording video and in regular operation
* Manual reset of OTEStamper
* Make mount panel user configurable for J2000 or JNOW (Steve)
* Update image in response to check boxes without requiring image to be retaken
* Refactor "evolved" CameraModel.py into a command based system and decouple everything so everything runs as a command, updating the UI as appropriate.  This will also get ready for command based operation/scripting. (similar approach to Siril)
* Change to Indi Neurtral https://www.indilib.org/api/classINDI_1_1Telescope.html
* Put target on screen to show the star.
* Star Catalogues HIP, TYC (Tycho 2), UCAC4, G-RADEC, (XZ, ZC - Use RADEC instead).  Dave Herald has a catalogue for occultations.  See also catalogues in Siril: https://siril.readthedocs.io/en/latest/astrometry/annotations.html
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