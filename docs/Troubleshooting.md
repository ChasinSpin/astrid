# Troubleshooting

* [Host Not Found](#host-not-found)
* [GPS Poor Reception](#gps-poor-reception)
* [Mouse Problems On Tablet](#mouse-problems-on-table)
* [Simbad Planets Inaccurate](#simbad-planets-inaccurate)
* [Indi Testing](#indi-testing)
* [Tuning GPS PPS Offset](#tuning-gps-pps-offset)
* [GPS Accuracy](#gps-accuracy)

## Host Not Found

It can take a few minutes for astrid.local to be pushed to the device you are 
connecting from's DNS.

## GPS Poor Reception

A good solid GPS signal is required for both timing and positioning.  If the Timing/GPS buttons are not constantly Green in Astrid, then you should look into the positioning of the GPS antenna. It is suggested to mount the antenna facing the sky and with a clear view of it.  Mounting the antenna on the telescope is not recommended because most tubes are metal or carbon fiber and the reception will be poor, the telescope also moves and that can cause the view of the sky to change for the GPS receiver.  Equally, mounting too close to the tripod or electronics may interfere with reception.

**It's not recommended to record an occultation unless Site, GPS, Timing and Acquisition buttons are Green.  A GPS/Timing button that changes to Red during a recording can produce incorrect timing.**
	
## Mouse Problems On Tablet

If you have to move the mouse on a tablet to be able to select a button, enter text into a field etc., then change "Interactive" to "Touch Panel" in your VNC settings.

## Simbad Planets Inaccurate

Planets looked up on Simbad have incorrect RA/DECs, for now use other software to determine RA/DEC and input manually.

## Some spots on VNC are blurred

This is due to the compression be used when automatic compression is set for the connection in VNC. You can choose to use less compression at the expense of a slower connection / responsiveness.

## Brightness Of Image Changes when Selecting "Display" Options

This is a limitation of the display pipeline and GPU.  This does not affect saved data in an yway.
	
## Indi Testing
		#indiserver -v -m 100 indi_lx200am5     # All drivers are in /usr/bin
		#indi_setprop "ZWO kjjAM5.CONNECTION_MODE.CONNECTION_SERIAL=On"
		#indi_setprop "ZWO AM5.DEVICE_PORT.PORT=/dev/ttyACM0"
		#indi_setprop "ZWO AM5.CONNECTION.CONNECT=On"
		#indi_getprop
		#indi_setprop "ZWO AM5.GO_HOME.GO=On"
				
## Tuning GPS PPS Offset
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