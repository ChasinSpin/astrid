# Astrid Mini Display

## Introduction

The Astrid Mini Display is a small device with a display that displays Astrid's current network settings.

It connects over USB (USB2 or USB3), and its buttons can be used to switch between Hotspot and WiFi router mode.

In the future, it will be used to provide additional functionality.

Only 1 Astrid Mini Display is required for all your Astrids, it doesn't have to be connected for Astrid to start, and can be removed and plugged into another Astrid whilst both are running.

## Requirements

USB-B to USB-C cable with both power **AND DATA** is required.

Astrid Mini Display can use either:
	
* [Adafruit ESP32-S2 Reverse TFT Feather](https://www.adafruit.com/product/5345)
* [Adafruit ESP32-S3 Reverse TFT Feather](https://www.adafruit.com/product/5691)

## Initial Installation / Upgrading

Plug in the Astrid Mini Display to Astrid, and in "Astrid Tools", double click/tap on "Install Mini Display" and follow the instructions.

## Usage

The Mini Display contains 4 buttons: 3 user buttons and 1 reset button (which resets the Mini Display only).

Currently, to switch between Astrid Hotspot and Regular Wifi modes, you press anyone of the group of 3 buttons.  The press has to be deliberate, a fast tap will be ignored to avoid accidental triggering.

When switching modes, you should press the button and wait; soon, a gray message will be displayed indicating that it is switching; please wait as it switches.  Switching networks is quite involved and takes time; be patient; Astrid will update you as it makes connections to the network. First, it will connect to the Wi-Fi network, and then it will be allocated an IP address. You can connect after you see the IP address allocated, if you try to make a connection with VNC before that, the connection will fail.  If the Wifi is not connected to or an IP address is not allocated then there is a problem with the WiFi router you are using that you should investigate.

If you fail to connect to your WiFi network (for example, wrong password), then you can always press the button again to return to Astrid Hotspot mode to fix it.

## Troubleshooting

Q. Display lights, but you can't install the software

A. Be sure that the USB cable you are using provides both power AND DATA (try another cable)

## Bitmap (Developer only)

* Export to png and open in Photoshop
* Resize to 240x135
* Image / Mode / Indexed Color
	* Palette: Local (Selective)
	* Colors: 256
	* Forced: None
* File / Save As Copy / BMP
	* Windows
	* 8 bit
	* (nothing checked)