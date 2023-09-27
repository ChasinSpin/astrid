# Cameras

## Introduction

* [Raspberry Pi HQ](https://www.raspberrypi.com/documentation/accessories/camera.html)

		
	| Name | Value | 
	| ---- | ----- |
	| Sensor model | Sony IMX477R Exmor RS CMOS |
	| Architecture | Back-Illuminated(R), Stacked(S) |
	| Mono/Color | Color |
	| Shutter | Rolling |
	| Pixel size | 1.55um x 1.55um |
	| Bits | RAW12/10/8, COMP8 |
	| Sensor resolution | 4056 x 3040 (12.3 Megapixels) |
	| Sensor image area | 6.287mm x 4.712mm|
	| Sensor diagonal | 7.9mm | 
	| Optical size | 1/2.3" |
	| Binning | 1x or 2x |
	| Dynamic range | [11.15 stops](https://www.strollswithmydog.com/tag/imx477/) |
	| Read noise | [3e(gain 1), 1.5e(gain 16)](https://www.strollswithmydog.com/tag/imx477/) |
	| Quantum efficiency | TBD |
	| Gain | 1-22.25 |
	| Maximum exposure time | 667-694s |
	| Minimum exposure time | 31-114us |
	| IR cut filter | [Hoya CM500](http://unihedron.com/projects/darksky/hcm500.htm) - [Removable, see "Filter Removal"](https://www.raspberrypi.com/documentation/accessories/camera.html) |
	| Mode: 0| Size:(1332,990) Bin:2 Bits:10 FOV:(65.7%,65.1%) MaxFPS:120.05 Exp:31us->667s |
	| Mode: 1 | Size:(2028,1080) Bin:2 Bits:12 FOV:(100.0%,71.1%) MaxFPS:50.03 Exp:60us->674s |	| Mode: 2 | Size:(2028,1520) Bin:2 Bits:12 FOV:(100.0%,100.0%) MaxFPS:40.01 Exp:60us->674s |	| Mode: 3 | Size:(4056,3040) Bin:1 Bits:12 FOV:(100.0%,100.0%) MaxFPS:10.00 Exp:114us->694s |
	| Camera Datasheet | [Raspberry Pi High Quality Camera](https://static.raspberrypi.org/files/product-briefs/Raspberry_Pi_HQ_Camera_Product_Brief.pdf)|
	| Sensor Datasheet | [IMX477-AACK-C](https://www.uctronics.com/download/Image_Sensor/IMX477-DS.pdf) (IMX477R is a Raspberry Pi version, this is the closest sensor datasheet)|
	| Raspberry Pi Documentation | [Cameras](https://www.raspberrypi.com/documentation/accessories/camera.html) |
		
* [Global Shutter Camera](https://www.raspberrypi.com/documentation/accessories/camera.html)

	| Name | Value | 
	| ---- | ----- |
	| Sensor | Sony IMX296LQR-C Pregius Gen 2 |
	| Architecture | Front Illuminated |
	| Mono/Color | Color |
	| Shutter | Global |
	| Pixel size | 3.45um x 3.45um |
	| Bits | RAW10 |
	| Sensor resolution | 1456 x 1088 (1.58 Megapixels) |
	| Sensor image area | 5.023mm x 3.754mm|`
	| Sensor diagonal | 6.3mm | 
	| Optical size | 1/2.9" |
	| Binning | 1x |
	| Dynamic range | TBD|
	| Read noise | [2.2e](https://scientificimaging.com/knowledge-base/qe-curves-for-cmos-imagers/) |
	| Dark current @ 25C| [3.2e/p/s](https://scientificimaging.com/knowledge-base/qe-curves-for-cmos-imagers/) |
	| Full well capacity| [10.6Ke](https://scientificimaging.com/knowledge-base/qe-curves-for-cmos-imagers/) |
	| Quantum efficiency | [Peak QR: 68% @ 550nm](https://scientificimaging.com/knowledge-base/qe-curves-for-cmos-imagers/) |
   	| Gain | 1-16 |
	| Maximum exposure time | 15.534385s |
	| Minimum exposure time | 29uS |
	| IR cut filter | Yes - [Removable, see "Filter Removal"](https://www.raspberrypi.com/documentation/accessories/camera.html) Filter type unknown, but maybe [Hoya CM500](http://unihedron.com/projects/darksky/hcm500.htm) i.e. same as HQ camera  |
	| Mode: 0 | Size:(1456,1088) Bin:1 Bits:10 FOV:(100%,100%) MaxFPS:60.38 Exp:29us->15.534385s |
	| Camera Datasheet | [Raspberry Pi Global Shutter Camera](https://datasheets.raspberrypi.com/gs-camera/gs-camera-product-brief.pdf)|
	| Sensor Datasheet | [Full Datasheet](https://en.sunnywale.com/uploadfile/2023/0327/IMX296LQR-C_Fulldatasheet_Awin.pdf); [Summary Datasheet IMX296LQR](https://scientificimaging.com/wp-content/uploads/2021/01/FSM-IMX296_V1A-V1B_Datasheet_v1.1b_Full.pdf) |
	| Raspberry Pi Documentation | [Cameras](https://www.raspberrypi.com/documentation/accessories/camera.html) |

## Camera Notes

### 	Raspberry Pi HQ:

#### XVS Trigger Mode

Sony IMX477 Sensor, by default XVS (active low) are disabled - ** 1.8V ** when a frame starts to be read out.  XVS is for the start of the frame (vertical).  Frame being read out is at the end of the exposure, so subtract exposure length to get frame starting time.  To enable, add to /boot/cmdline.txt:

	 imx477.trigger_mode=1  
	 
However for old camera model (not picamera2), use this: [Old Camera Mode Configuration](https://forums.raspberrypi.com/viewtopic.php?t=281913)
[Readout example (not this sensor)](https://www.sunnywale.com/uploadfile/2021/1227/IMX174LLJ-C-Awin.pdf)
[Configuring Registers](https://forums.raspberrypi.com/viewtopic.php?t=319373)

#### Star Eater (Defective Pixel Control - DPC)

Sony IMX477 Sensor, by default Star Eater is enabled which will reduce noise but has the side effect of eating stars which has been well documented in some Sony Cameras.  To disable, add to /boot/cmdline.txt:

	imx477.dpc_enable=0
	
[Defective Pixel Control](https://forums.raspberrypi.com/viewtopic.php?t=341862)

### 	Raspberry Pi Global Shutter:

Sony IMX296 Sensor, by default XVS and XHS output triggers (active low) are enabled - ** 1.8V ** when a frame starts to be read out.  XVS is for the start of the frame (vertical) and XHS is for the start of a horizontal scan line (row readout).  Frame being read out is at the end of the exposure, so subtract exposure length to get frame starting time.

[Closest Datasheet](https://www.leopardimaging.com/uploads/LI-IMX296-MIPI-CS_datasheet.pdf)

# Links

LibCamera

* [Picamera2 Library](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
* [Picamera2 Examples](https://github.com/raspberrypi/picamera2/tree/main/examples)
* [Picamera2 Overview](https://raspberrytips.com/picamera2-raspberry-pi/)

Camera

* [Hubble Pi - HQ Camera and Code to Read It](https://magpi.raspberrypi.com/articles/hubble-pi)
* [Adding Timestamps to libcamera-vid](https://forums.raspberrypi.com/viewtopic.php?t=326796)
* [libcamera](https://www.raspberrypi.com/documentation/computers/camera_software.html)
* [Global Shutter Camera](https://hackaday.com/2023/03/09/new-raspberry-pi-camera-with-global-shutter/)
* [QE Curves - CMOS Images Sony](https://scientificimaging.com/knowledge-base/qe-curves-for-cmos-imagers/)
* [Sony IMX296 Sensor](https://www.phase1vision.com/sensors/sony-sensors/pregius/imx296llr)
* [Global Shutter Camera Datasheet (Raspberry Pi)](https://datasheets.raspberrypi.com/gs-camera/gs-camera-product-brief.pdf)
* [ArduCam libcamera](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/Libcamera-User-Guide/)
* [Raspberry Pi Camera Software](https://www.raspberrypi.com/documentation/computers/camera_software.html)

Star Eater

[New Driver need to edit in cmdline.txt](https://forums.raspberrypi.com/viewtopic.php?t=341862)
[Overview 1](https://forums.raspberrypi.com/viewtopic.php?t=278439)
[Overview 2](https://forums.raspberrypi.com/viewtopic.php?t=277768)
[Overview 3](https://www.strollswithmydog.com/pi-hq-cam-sensor-performance/)
