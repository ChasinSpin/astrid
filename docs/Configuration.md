# Configuration

##### Note: It's strongly recommended to use the "Settings" button when Astrid is launched to change settings.  This remains for reference and documentation for the effect of each setting.

## Introduction

Config files are stored in /media/pi/ASTRID/configs and organized as follows:
	
	* /media/pi/ASTRID/configs/observer.json
	* /media/pi/ASTRID/configs/occultations.json
	* /media/pi/ASTRID/configs/objects.json
	* /media/pi/ASTRID/configs/configs.json	* /media/pi/ASTRID/configs/config1/
		* astrometry.cfg
		* camera.json
		* mount.json
		* platesolver.json
		* site.json	[Optional] 
	* /media/pi/ASTRID/configs/config2/
		* astrometry.cfg
		* camera.json
		* mount.json
		* platesolver.json
		* site.json	[Optional] 

		
File formats:

* [configs.json](#configs)
* [astrometry.cfg](#astrometry)
* [camera.json](#camera)
* [general.json](#general)
* [mount.json](#mount)
* [objects.json](#objects)
* [observer.json](#observer)
* [occultations.json](#occultations)
* [platesolver.json](#platesolver)
* [site.json](#site)

Note: You may find it easier to validate any JSON with an online validator in case of errors in entry.

## configs

This config.json file is used to present the selection of configs when Astrid is launched.

	{
    	"configs": [
        	{
            	"configFolder": "nexstar_6se_0.7X_eq5",
            	"summary": "6SE/AZ-EQ5 with 0.7X",
            	"mount": "Sky-Watcher AZ-EQ5",
            	"telescope": "Celestron NexStar 6SE",
            	"focalreducers": "Celestron 0.7X"
        	},
        	{
            	"configFolder": "edgehd_0.7X_0.5X_am5",
            	"summary": "EdgeHD/AM5 with 0.7X Celestron and 0.5X IOTA",
            	"mount": "ZWO AM5",
            	"telescope": "Celestron EdgeHD 9.25\"",
            	"focalreducers": "0.7X Celestron and IOTA 0.5X"
        	},
        	{
            	"configFolder": "simulator",
            	"summary": "Simulator",
            	"mount": "Simulator",
            	"telescope": "Simulator",
	            "focalreducers": "None"
        	}
    	],
    	"selectedIndex": 1
    }

| Variable | Description |
| -------- | ----------- |
| configFolder | Sub folder of the configs folder.  This must match exactly the folder name the rest of the settings are stored wihin. |
| summary | Short unique summary describing the scope to the user to enable a config to be selected. |	
| mount |	Longer description of the mount. |
| telescope | 	Longer description of the telescope. |
| focalreducers | Longer description of the focal reducer(s). |
| selectedIndex | Index of the currently selected configuration. 0 based (first config entry is index 0, next is 1 etc.) |


## astrometry

The astrometry.cfg file is used primarily to specify the index files to use for platesolving, and is the config file for the astrometry.net platesolver (solve-field).  Index files are stored locally in the astrometry folder on the USB Flash Drive (i.e. the solver is offline and doesn't require the internet).

astrometry.cfg is created as required based on the focal length and camera chosen in Astrid.  There is no need to create it or edit it.

## camera

The camera.json file stores configuration related to the camera:

	{
		"mode_selected": 1,
		"hflip": false,
		"vflip": false,
		"gain": 4.0,
		"accelerated_preview": false,
		"photo_format": "fit",
		"radec_format": "hmsdms",
		"polar_align_test": false,
		"polar_align_rotation": 90.0,
		"default_photo_exposure": 5.0,
		"prompt_dark_after_acquisition": true,
		"dither_ra": 0.0010,
		"dither_dec": 0.0100,
		"photosFolder": "/media/pi/ASTRID/Photo",
		"videoFolder": "/media/pi/ASTRID/OTEVideo",
		"buzzer_enable": true
	}
	
| Variable | Description |
| -------- | ----------- |
| mode_selected | Cameras have multiple modes with different attributes (size, binning etc.). Suggested modes: IMX296 Mono/Pi GSC: 1, Pi HQ: 3 |
| hflip | Set to true to horizontally flip the image, otherwise false. |
| vflip | Set to true to vertically flip the image, otherwise false. |
| gain | Gain should be optimized to the sensor for read noise as some cameras have dual gain circuits.  Suggested: IMX296 Mono/Pi GSC: 4.0, Pi HQ: 16.0 |
| accelerated_preview | Set to true to use the graphics chip to accelerate the preview image in Astrid, otherwise false. It is suggested to set to false to avoid issues with VNC viewers. |
| photo_format | Unused, must be set to "fit" |
| radec_format | This is the format for the way RA/DEC are presented visually to the user. "hmsdms" = Hours Minutes Seconds(RA) and Degrees Minutes Seconds (DEC). "hour" = 24 Hour RA and "deg" = 360 degree RA |
| polar\_align\_test | If set to "true", test files for the Polar Alignment routine are used from so that it can be tested during daylight hours. Ordinarily set to false unless testing.|
| polar\_align\_rotation | The number of degrees to rotate the scope during polar alignment.  This should be no more than 90.0 degrees and should not be less than 60.0 degrees. 90.0 degrees is the suggested value for accurate polar alignment. |
| default\_photo\_exposure | This is the default exposure in seconds provided in the exposure box in Astrid.  It suggested that this should be set to the exposure that is needed to get a consistant plate solve, e.g. 1.0 - 5.0 seconds. |
| prompt\_dark\_after\_acquisition | If set to true, a message box prompts the use to record 100 frames of dark video after an acquisition |
| dither_ra / dither_dec) | When the box is checked and "# Subs" is greater than 1, this value is used to randomly dither in RA/DEC to prevent walking noise when stacking.  The values are in degrees and represent the maximum the position can be dithered |
| photosFolder | Location to store fits files taken in Task = Photo Mode, set to "/media/pi/ASTRID/Photo" |
| videoFolder | Location to store RAVF files (video files) taken in Task = OTE Video "/media/pi/ASTRID/OTEVideo" |
| buzzer_enable | Buzzer beeps in the prior 6 seconds to auto record if true |

## general

The general.json file stores configuration related general settings:

	{
		"fan_mode": "on",
		"center_marker": "small cross"
	}
	
| Variable | Description |
| -------- | ----------- |
| fan_mode | on = fan always on; idle = fan on when not recording; off = fan off. If you're experiencing vibration effects with long focal lengths, or you are imaging in extreme cold and want to retain heat, this setting can be used.  Note: Although the Raspberry Pi should reduce speed if it gets too hot, there's a slim possibility of damage.  If you live in a hot climate, or it's inside, you probably want the fan on all the time. It is suggested that if considering switching the fan off, then the Raspberry Pi should have the heat sinks installed. |
| center_marker | When "Center Marker" is checked the displayed marked can be one of: crosshairs; rectangle or "small cross" |

## mount

The mount.json file stores configuration related to the mount:

	{
		"name": "ZWO AM5",
		"indi_module": "indi_lx200am5",
		"indi_telescope_device_id": "ZWO AM5",
		"indi_usb_tty": "/dev/ttyACM0",
		"baud": 9600,
		"align_axis": "eq",
		"goto_capable": true,
		"tracking_capable": true,
		"mount_is_j2000": false,
		"local_offset": "0.00",
		"parkmethod": "home",
		"debug": false
	}
	
| Variable | Description |
| -------- | ----------- |
| name | How the mount appears in the Mount Panel in Astrid under "Name".  Choose something short so that the name doesn't wrap in the panel. e.g. "ZWO AM5" |
| indi_module | The IndiLib dirver executable needed for the mount. The required executable can be determined with [IndiLib Telescopes](https://www.indilib.org/devices/telescopes.html) under "Listing Details" and "Driver Executable". Most mounts have been added to Astrid, and the presence of a driver executable can be found by looking in /usr/bin.  e.g. "indi_lx200am5". |
| indi\_telescope\_device\_id | This is the device is that shown when indi\_getprop is run.  For example for an indi_getprop output of: "ZWO AM5.CONNECTION.CONNECT=Off", then this should be set to "ZWO AM5" |
| indi\_usb\_tty | The unix USB (serial port) the driver should connect to. Common values are "/dev/ttyUSB0" and "/dev/ttyACM0".  Connected port can be checked with dmesg, although it's suggested to try "/dev/tty/USB0" first as it's the most common.  (ZWO AM5 uses "/dev/ttyACM0"). |
| baud | The baud rate the USB (serial port) communicates at.  Common values are 9600 and 115200. |
| align\_axis | "eq" for Equatorially mounted telescopes and "altaz" for Alt-Azimuth mounted telescopes. |
| goto\_capable | true if the mount is capable of goto in 2 axis, or false if not. |
| tracking\_capable | true if the mount is capable of following a target with the earth's location|
| mount\_is\_j2000 | Set to true if this mount expects j2000 coordinates for syncs and gotos.  Ordinally most mounts are JNOW, and this should be set to false. |
| local\_offset | This is the timezone offset between UTC and local time (negative numbers are West of Greenwich, London, UK).  It is recommended to set this value to "0.00" for most mounts and is just provided as a convenience if your mount is broken in its implementation and requires the offset to be specified too. The symptom of a broken mount would be if the RA on goto's was off by the number of hours for your local timezone. Ordinarily, Sidereal time is calculated based on your Longitude (Site information), not timezone offset. |
| parkmethod | "park" or "home". The method used to park the scope. Most mounts use the telescope property "TELESCOPE\_PARK" in IndiLib (which can be verified with indi\_getprop) and this setting should be set to "park". An exception would be something like the "ZWO AM5" which uses "GO_HOME" and this should be set to  "home". |
| debug | If set to true, debugging information (commands sent to the mount, and information received from the mount) is output which can be useful when setting up new mounts. Ordinarily, this should be set to false. |

## objects

The objects.json file stores custom objects (targets). These objects can also be used when not connected to the internet. It is strongly suggested that these are not manually entered in this json and are entered via Astrid's Object (ICRS) panel.  All RA/DECs are in 360 degree ICRS/J2000:

	{
    	"custom_objects": [
        	{
            	"name": "Vega",
            	"ra": 279.234734787,
            	"dec": 38.783688956
        	},
        	{
            	"name": "Arcturus",
            	"ra": 213.915300295,
            	"dec": 19.182409162
        	}
    	]
	}
	
| Variable | Description |
| -------- | ----------- |
| name | The name of the object |
| ra | The 360 deg RA of the object|
| dec | The DEC of the object |

## observer

The observer.json file stores information about the observer, this information is used to provide observer information in the RAVF (video files):

	{
		"observer_name": "John Doe",
		"observer_id": "johndoe@example.com",
		"owcloud_login": "johndoe@example.com",
		"owcloud_password": "password"
	}
	
| Variable | Description |
| -------- | ----------- |
| observer\_name | Set to the name of the observer (generally you). |
| observer\_id | Set to the observer id. This could be email address, a number etc. |
| owcloud\_login | Set to the owcloud login, usually email address |
| owcloud\_password | Set to the owcloud password |

## occultations

The occultations.json file stores occultations (targets). These objects can also be used when not connected to the internet. It is strongly suggested that these are not manually entered in this json and are entered via Astrid's Object (ICRS) panel.  All RA/DECs are in 360 degree ICRS/J2000.  Occelmnt data is also stored when provided:

	{
    	"occultations": [
        	{
            	"name": "Petrina",
            	"ra": 334.3794887916667,
            	"dec": 0.6233059000000001,
            	"event_time": "2023-08-16T08:42:24",
            	"occelmnt": {
                	"Occultations": {
                    	"Event": {
                        	"Elements": "JPL#81:2023-07-30@2023-08-16[OWC],3.90,2023,8,16,8.706836,-0.330947,0.439776,-5.300154,-3.988511,-0.000865,-0.001414,0.000001,0.000000",
                        	"Earth": "-120.4068,0.7422,50.50,13.77,False",
                        	"Star": "TYC 559-01642-1,22.29196592,0.6233059,11.73,11.47,11.05,0.0,0,,22.31233020,0.7421805,1.82,1.80,0,0,0",
                        	"Object": "482,Petrina,13.07,45.8,1.8647,0,0,-1.667,-18.81,,2.4,0",
                        	"Orbit": "0,53.9673,2023,8,16,87.9178,179.3705,14.4736,0.09643,2.99829,2.70917,8.97,5.0,0.15",
                        	"Errors": "1.152,0.0107,0.0003,82,0.0052,Known errors,0.85,0,-1,-1",
                        	"ID": "20230816_1642-1,60157.39"
                    	}
                	}
            	}
        	}
    	]
	}

| Variable | Description |
| -------- | ----------- |
| name | Name of the event (this is the name that can be searched for in Astrid's Object (ICRS) panel. |
| ra | 360 degree RA of the target |
| dec | DEC of the target |
| event\_time | Event time.  This can be center time of the event, or the time the event will happen locally. |
| occelmnt | This is the occelmnt data for the event and is best entered via Astrid / Object (ICRS)/ Database: Occultations / Add to populate.  The Occelmnt data input via that method, can be cut and poasted from "OW Cloud", "Steve Prestons Predictions", or any other method that can output occelmnt data. |

## platesolver

The platesolver.json file stores configuration related to platesolving:

	{
		"focal_length": 732.0,
		"search_radius_deg": 5.0,
		"limit_objs": 1000,
		"downsample": 2,
		"source_extractor": true,
		"scale_low_factor": 0.1,
		"scale_high_factor": 1.25,
		"direction_indicator_polar_align": 2,
		"direction_indicator_platesolve": 1
	}
	
| Variable | Description |
| -------- | ----------- |
| focal\_length | The focal length of the telescope with all the focal reducers and optics in millimeters (floating point number).  When first setting up a scope, this can be estimated provided the actual scope focal length falls between scale\_low\_factor x focal\_length and scale\_high\_factor x focal\_length. Once a platesolve has been achieved, the actual focal length will be reported and this value should be updated to match the platesolve focal length for faster solves. Plate solves outside this focal length range will never solve.|
| search\_radius\_deg | The search radius in degrees for plate solves from the position the scope thinks it is currently at, or the RA/DEC stored in a fits file loaded. This setting is only used when "Full Sky Solve" is not checked.  This allows for faster solves when the scope knows it's position.  A suggested value is 5.0 |
| limit\_objs | The --objs number provided to [solve-field](https://manpages.debian.org/testing/astrometry.net/solve-field.1.en.html) and cuts the source list down to at least this many source. Suggested value is 1000. |
| downsample | Images can be downsampled by a factor to speed up platesolving and increase signal to noise. See [Downsample](https://manpages.debian.org/testing/astrometry.net/solve-field.1.en.html). No downsampling: 1, 2X downsampling: 2. Suggested value is 2 |
| source\_extractor | If set to true, it uses Source Extractor rather than image2xy to detect stars. Set to false otherwise. Source Extractor is slower, but seems to perform better. See [Extractor](https://manpages.debian.org/testing/astrometry.net/solve-field.1.en.html).  Suggested value is true. |
| scale\_low\_factor | This value multiplied by the focal length is the lowest focal length to consider when platesolving.  Suggested value is 0.1 |
| scale\_high\_factor | This value multiplied by the focal length is the highest focal length to consider when platesolving.  Suggested value is 1.25 |
| direction\_indicator\_polar\_align | During polar alignment, arrows can be displayed to indicate the direction to adjust the mount. "None", "1 Arrow", "2 Arrows" |
| direction\_indicator\_platesolve | When the "Plate Solve" button is hit, and an Object is selected, arrows can be displayed to indicate the direction to adjust the pointing of the scope to reach the target.  This is particularly useful when using a scope without goto. "None", "1 Arrow", "2 Arrows" |

## site

The site.json file stores information related to the current site. This file is optional, and is updated when the "Site" and "Update Site and Mount" buttons are pressed.  If this JSON file does not exist, Astrid will default it to a 0.0, 0.0 location and the "Site" button will be Red until the user selects "Update Site and Mount".  This file can be safely deleted for privacy when backing up or transferring config files:

	{
    	"name": "Local",
    	"latitude": 58.3489123,
    	"longitude": -82.3829384,
    	"altitude": 1102.1
	}
	
| Variable | Description |
| -------- | ----------- |
| name | The name of the site.  This is for future use and currently should be set to "Local". |
| latitude | Latitude of the site. |
| longitude | Longitude of the site. (negative numbers are west of Greenwich, London, UK).|
| altitude | Altitude of the site in meters (floating point number). |