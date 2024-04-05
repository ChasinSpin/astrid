# Troubleshooting

## Support

Astrid is supported on a **best-effort** basis as time permits, you should not expect support for Astrid. It is an open-source project and the code is available for you to add new features or fix issues.

**Please check the documentation first.**

**The aim is to document everything to reduce support requirements from a real person. The scope of this project is large and we ask for your assistance, by adhering to the following:**

Any request for support assistance has the following requirements:

* You are running the latest version of Astrid
* Astrid is being used within it's specifications
* Design/new feature requests are suggestions only
* No support for WiFi routers

### That is:

* Requests for help or bug fixes on older versions will be asked to upgrade first and try again
* Problems with videos frame rates > 30fps, will be referred back to the specifications and the alert that was received when you recorded
* If you purchased a battery power pack and are having power issues, then you'll be pointed to the documentation for Power Supplies
* Problems with GPS reception will be pointed to the documentation
* If you can't connect to WiFi, then find someone local for help

### You can help:

You can help reduce the support load by taking the time to check the documentation first and keeping the software up to date.

Astrid follows a Rapid Development model, and all bug fixes are by new versions, not by going backwards.  There is no regression path or change control, GitHub stores the code changes, and the path is always forging forward.


## Common Issues and Solutions

* [Host Not Found](#host-not-found)
* [Site Button Is Orange Or Red](#site-button-is-orange-or-red])
* [GPS Poor Reception](#gps-poor-reception)
* [Mouse Problems On Tablet](#mouse-problems-on-table)
* [Android Host Not Found](#android-host-not-found)
* [Indi Testing](#indi-testing)
* [Tuning GPS PPS Offset](#tuning-gps-pps-offset)
* [GPS Accuracy](#gps-accuracy)
* [Intermittent Power](#intermittent-power)
* [Lines On Video](#lines-on-video)
* [Mount or Prepoint Has Wrong Position](#mount-or-prepoint-has-wrong-position)
* [Linking to OWCloud Events Fails](#linking-to-owcloud-events-fails)
* [Wrong Password Entered For WiFi and Unable To Connect](#wrong-password-entered-for-wifi-and-unable-to-connect)


## Host Not Found

It can take a few minutes for astrid.local to be pushed to the device you are 
connecting from's DNS.

Make sure you are on the correct WiFi network, the ethernet port flashes alternate Green/Yellow when connected to a known WiFi Network and is solid Green/Yellow when Astrid is generating it's own Wifi Hotspot (Adhoc Network).

The hostname astrid.local is mapped via a process called mDns/Bonjour which may not work on older computers or poorly designed Wifi Routers. Use the IP address instead to connect if this is an issue with your hardware

Mini Display can be used to see your current network configuration and to switch to your Home WiFi.

## Site Button Is Orange Or Red

To change the Site Button from Orange/Red to Green, click on the button and click "Update Site and Mount".  The Orange/Red is due to a mismatch between the last time the "Update Site and Mount" button was clicked and position the GPS is reporting now.  

It is natural for GPS to change position over time by a small amount, so Orange is not an issue for acquisitions that don't need super precision (like NEOs).  Everytime you move to a new site, you will need to click the "Update Site and Mount" button.

## GPS Poor Reception

A good solid GPS signal is required for both timing and positioning.  If the Timing/GPS buttons are not constantly Green in Astrid, then you should look into the positioning of the GPS antenna. It is suggested to mount the antenna facing the sky and with a clear view of it.  

Possible reasons for poor reception are:

* Antenna upside down (black part not pointing to the sky)
* Antenna substituted for another. Only the recommended antenna should be used, other antennas may look the same but are inferior
* Usage inside (the top floor of a house may work depending on construction, but outside is better)
* Obstructed view of the sky (trees, buildings, etc.), GPS requires a clear 360-degree view of the sky
* Placed on metal. Although the antennas are magnetic, the metal often creates a ground plane and can make reception unpredictable; avoid metal other than a nail or a bolt
* Placed on the ground. Ground is an unpredictable ground plane; often, grass/dirt interferes with the signal, and a concrete slab may not, experience varies, avoid
* Attached to a telescope. Telescopes move and are often metal or carbon fiber, all of which will interfere with signal reception
* Poor cable connection. Ensure the antenna cable is fully screwed in and the antenna hasn't disconnected from the GPS receiver
* Broken antenna. GPS cables can be damaged, Antenna drops, and pins damaged/corroded.  There is also a Pigtail inside Astrid they may become loose or damaged.

**It's not recommended to record an occultation unless Site, GPS, Timing and Acquisition buttons are Green (with the exception of an Orange Site Button).  A GPS/Timing button that changes to Red during a recording can produce incorrect timing.**
	
## Mouse Problems On Tablet

If you have to move the mouse on a tablet to be able to select a button, enter text into a field etc., then change "Interactive" to "Touch Panel" in your VNC settings.

## Android Host Not Found

Newer Androids support the mDNS/Bonjour protocol, such that hostnames with .local in can be resolved.  However older androids do not support this, so please upgrade your OS to the latest version.

## Some spots on VNC are blurred

This is due to the compression being used when automatic compression is set for the connection in VNC. You can choose to use less compression at the expense of a slower connection / responsiveness. Don't worry astrid always records the raw data from the camera.

## Brightness Of Image Changes when Selecting "Display" Options

This is a limitation of the display pipeline and GPU.  This does not affect saved data in an way.
	
## Indi Testing
### (Developer use only)
		#indiserver -v -m 100 indi_lx200am5     # All drivers are in /usr/bin
		#indi_setprop "ZWO kjjAM5.CONNECTION_MODE.CONNECTION_SERIAL=On"
		#indi_setprop "ZWO AM5.DEVICE_PORT.PORT=/dev/ttyACM0"
		#indi_setprop "ZWO AM5.CONNECTION.CONNECT=On"
		#indi_getprop
		#indi_setprop "ZWO AM5.GO_HOME.GO=On"
				
## Tuning GPS PPS Offset
### (Developer use only)

	Important: GPS and PPS signals must be within 200ms of each other (use offset to adjust), otherwise the PPS signal will be ignored, so we start with an offset of 0.1s
	
	Tuning GPS(NMEA) Offset:
		sudo vi /etc/chrony/chrony.conf
			# Disable reflock lines and use these
			refclock SHM 0 refid NMEA precision 1e-1 offset 0.1 noselect
			refclock PPS /dev/pps0 refid PPS lock NMEA precision 1e-9 offset 0.0 prefer
		sudo systemctl restart chrony
		# Monitor for PPS to get an asterisk by it (source selected) using:
		chronyc sources -v
		# Then when the source is selected, use the following and monitor offset for NMEA until it's stabilized and has reasonable std dev (<1ms)
		chronyc sourcestats -v
		# If offset is +35ms, then add +35ms to offset 0.1 for the NMEA refclock to become 0.135
		sudo vi /etc/chrony/chrony.conf
		sudo systemctl restart chrony
		
		chronyc sourcestats -v
		# Take the offset field for NMEA (136ms in this) case and ammend line to:
		refclock SHM 0 refid NMEA precision 1e-1 offset 0.136 noselect
		sudo systemctl restart chrony
		** REPEAT ** until NMEA Offset is sub 1ms
		
		# sourcestats is the offset of the source, sources is the offset from the system clock 
		
		To turn chrony tracking log on, uncomment:
			log tracking measurements statistics
			in /etc/chrony/chrony.conf
			sudo systemctl restart chrony
			log file is stored in /var/log/chrony/tracking.log
		
### Chronyc stages in tracking	
### (Developer use only)	

	pi@otestamper:~ $ chronyc tracking
	Reference ID    : 00000000 ()
	Stratum         : 0
	Ref time (UTC)  : Thu Jan 01 00:00:00 1970
	System time     : 0.000000000 seconds fast of NTP time
	Last offset     : +0.000000000 seconds
	RMS offset      : 0.000000000 seconds
	Frequency       : 14.883 ppm fast
	Residual freq   : +0.000 ppm
	Skew            : 0.000 ppm
	Root delay      : 1.000000000 seconds
	Root dispersion : 1.000000000 seconds
	Update interval : 0.0 seconds
	Leap status     : Not synchronised

	pi@otestamper:~ $ chronyc tracking
	Reference ID    : C6A1CB24 (198.161.203.36)
	Stratum         : 3
	Ref time (UTC)  : Sat Apr 01 05:52:47 2023
	System time     : 0.000565229 seconds slow of NTP time
	Last offset     : +0.005562202 seconds
	RMS offset      : 0.005562202 seconds
	Frequency       : 14.883 ppm fast
	Residual freq   : -511.255 ppm
	Skew            : 0.119 ppm
	Root delay      : 0.052770238 seconds
	Root dispersion : 0.007293095 seconds
	Update interval : 0.7 seconds
	Leap status     : Normal

	pi@otestamper:~ $ chronyc tracking
	Reference ID    : 50505300 (PPS)
	Stratum         : 1
	Ref time (UTC)  : Sat Apr 01 05:54:36 2023
	System time     : 0.000001976 seconds fast of NTP time
	Last offset     : +0.000001735 seconds
	RMS offset      : 0.004799102 seconds
	Frequency       : 14.891 ppm fast
	Residual freq   : +0.032 ppm
	Skew            : 0.198 ppm
	Root delay      : 0.000000001 seconds
	Root dispersion : 0.000019206 seconds
	Update interval : 31.0 seconds
	Leap status     : Normal
	

## GPS Accuracy

### (Developer use only)
	
### PPS on GPS:
	
GT-U7 (based on Neo 6m): [GPS-based Timing - Application Note](https://content.u-blox.com/sites/default/files/products/documents/Timing_AppNote_%28GPS.G6-X-11007%29.pdf)
	With positional fix, only needs 1 satellite, without needs 4 satellites.
	Average of 2.35ns over 6 hours, with a sampling deviation of 6.7ns
	
### Chrony + PPS:
 With 1/3 of the sky blocked and from a power off cold start, this is the speed at which timing was acquired:
 
*  0m 35s: -478ms (NTP Server)
*  1m 23s: -1.12ms (NTP Server, over Wifi and Shaw internet)
*  2m 29s:  -2.71ms (NTP Server, over Wifi and Shaw internet)
*  2m 55s: 6.15ms (First PPS GPS Lock, now Stratum 1)
*  3m 27s: -2.85uS (PPS, GPS Lock)
*  3m 59s: 770nS (PPS, GPS Lock)

		===================================================================================================================================
		   Date (UTC) Time     IP Address   St   Freq ppm   Skew ppm     Offset L Co  Offset sd Rem. corr. Root delay Root disp. Max. error
		===================================================================================================================================
		2023-04-01 04:11:34 0.0.0.0          0     21.770      0.016  0.000e+00 ?  0  0.000e+00 -9.664e-14  1.000e+00  1.000e+00  1.500e+00
		2023-04-01 04:12:09 45.61.49.156     3     21.770      0.016 -4.783e+01 N  3  5.660e-03 -2.854e-10  5.462e-02  1.035e-01  1.500e+00
		2023-04-01 04:12:57 45.61.49.156     3     21.770      0.016 -1.126e-03 N  2  3.774e-03 -5.652e-12  5.692e-02  3.702e-02  4.790e+01
		2023-04-01 04:14:03 217.180.209.214  2     21.770      0.016 -2.713e-03 N  1  3.433e-03 -1.585e-07  7.181e-02  3.587e-03  7.605e-02
		2023-04-01 04:14:29 PPS              1     21.770      0.016  6.169e-03 N  1  7.607e-07  2.144e-03  1.000e-09  2.426e-05  4.320e-02
		2023-04-01 04:15:01 PPS              1     21.769      0.029 -2.845e-06 N  1  5.378e-07 -7.400e-09  1.000e-09  2.135e-05  4.086e-03
		2023-04-01 04:15:33 PPS              1     21.763      0.060 -7.701e-07 N  1  1.033e-06 -2.143e-07  1.000e-09  2.329e-05  6.024e-05
		2023-04-01 04:16:05 PPS              1     21.746      0.111  7.365e-07 N  1  1.498e-06  3.563e-07  1.000e-09  2.778e-05  6.002e-05
		2023-04-01 04:16:37 PPS              1     21.741      0.119  2.519e-06 N  1  1.962e-06 -3.162e-07  1.000e-09  2.395e-05  6.469e-05
		2023-04-01 04:17:09 PPS              1     21.755      0.111  3.361e-06 N  1  2.249e-06 -1.042e-07  1.000e-09  2.431e-05  6.266e-05
		2023-04-01 04:17:41 PPS              1     21.824      0.122  8.528e-06 N  1  9.663e-07  9.403e-08  1.000e-09  2.528e-05  6.345e-05
		2023-04-01 04:18:13 PPS              1     21.849      0.062  1.476e-06 N  1  5.909e-07  4.371e-07  1.000e-09  2.035e-05  7.006e-05
		2023-04-01 04:18:45 PPS              1     21.853      0.035  4.704e-07 N  1  5.264e-07  2.600e-08  1.000e-09  2.106e-05  5.541e-05
		2023-04-01 04:19:17 PPS              1     21.857      0.028  7.900e-07 N  1  5.730e-07 -1.946e-07  1.000e-09  2.024e-05  5.463e-05
		2023-04-01 04:19:49 PPS              1     21.863      0.032  1.399e-06 N  1  7.986e-07  1.883e-09  1.000e-09  2.157e-05  5.415e-05
		2023-04-01 04:20:21 PPS              1     21.870      0.061  3.496e-06 N  1  1.070e-06  2.844e-08  1.000e-09  2.502e-05  5.604e-05
		2023-04-01 04:20:53 PPS              1     21.905      0.103  4.365e-06 N  1  9.487e-07  1.723e-10  1.000e-09  2.243e-05  6.317e-05
		2023-04-01 04:21:25 PPS              1     21.943      0.111  3.622e-06 N  1  1.010e-06 -2.883e-11  1.000e-09  2.165e-05  6.279e-05
		2023-04-01 04:21:57 PPS              1     21.970      0.072  2.306e-06 N  1  6.458e-07  1.574e-07  1.000e-09  2.499e-05  6.112e-05
		2023-04-01 04:22:29 PPS              1     21.987      0.060  1.924e-06 N  1  5.656e-07 -1.934e-11  1.000e-09  2.192e-05  6.151e-05
		2023-04-01 04:23:01 PPS              1     22.000      0.029  1.232e-06 N  1  2.788e-07 -2.347e-10  1.000e-09  1.853e-05  5.784e-05
		2023-04-01 04:23:33 PPS              1     22.007      0.040  1.156e-06 N  1  4.270e-07  8.070e-12  1.000e-09  2.174e-05  5.271e-05
		2023-04-01 04:24:05 PPS              1     22.014      0.036  5.754e-07 N  1  3.559e-07  1.679e-08  1.000e-09  2.130e-05  5.628e-05
		2023-04-01 04:24:37 PPS              1     22.018      0.025  2.773e-07 N  1  2.463e-07  1.091e-11  1.000e-09  2.195e-05  5.507e-05
		2023-04-01 04:25:09 PPS              1     22.014      0.042 -1.401e-06 N  1  6.271e-07 -6.953e-08  1.000e-09  2.176e-05  5.504e-05
		2023-04-01 04:25:41 PPS              1     22.007      0.055 -7.043e-07 N  1  5.887e-07 -1.249e-10  1.000e-09  2.425e-05  5.663e-05
		
## Intermittent Power

Astrid has a professional type DC Jack (for a long lifespan).  Often the cause of intermittent power is that the DC Plug has only been partially inserted so that plug is only retained lightly.  Please be sure to push the plug further past the initial resistance, so that it is fully inserted.

Another cause of intermittent power is a poor power supply that cannot supply the current required by Astrid.

Please note that intermittent power is bad for Astrid and can corrupt SD Cards and USB Flash Drives.

## Lines On Video

If you encounter intermittent lines on video, investigate where the Astrid was placed.  Do not place near High Voltage power lines, which are often along roads.

Although this hasn't been definitively demonstrated yet / seen in a recording, it has been seen a couple of times over a VNC connection at a specific site which had power lines directly above an Astrid.

It may impact either Wifi to the device running VNC, or induce into the sensitive CMOS sensor on the camera.

## Mount or Prepoint Has Wrong Position

The first thing to try is to take another photo, plate solve, and go, then repeat this process one more time; the star field should remain in a similar position, indicating the position is correct.

Other things to check (for example if Prepoint is an incorrect position), is your time and event details.

A valid GPS position, Time and site location are required for accurate positioning via a goto or prepoint.  Please ensure all status buttons are Green.

## Linking to OWCloud Events Fails

Some events may fail to link back to OWCloud.  Currently, OWCloud only supports IOTA-tagged events, and many of the predictions generated by Steve Preston in 2024 are not tagged due to the limitation of OWCloud to tag large numbers of events.  This is a limitation of OWCloud, and there are no plans at this time for OWCloud to support linking to non-IOTA tagged or events that are not tagged.  If you would like to see support for this, please contact the author of OWCloud directly.

## Wrong Password Entered For WiFi and Unable To Connect

If you enter the wrong password when setting up a WiFi network in Astrid (for example your Home WiFi), then when Astrid attempts to connect to that network, it won't be able to it.

Use the Mini Display to switch back to the Hotspot, and change your network password.

If you don't have the Mini Display, you will have to power cycle to gain access.