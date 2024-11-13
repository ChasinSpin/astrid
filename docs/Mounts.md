# Mounts

* [Introduction](#introduction)
* [Mounts and Connections Supported](#mounts-and-connections-supported)
* [Support](#support)
* [Mount Settings](#mount-settings)
* [Mount Testing And Verification](#mount-testing-and-verification)

## Introduction

Connecting your Goto Mount to Astrid may take some effort, especially if no one has set up the same or similar mount before. Many different mount manufacturers and mount models exist, and they lack consistency in operation, features, and requirements between them.

Astrid also does not require a Goto Mount and works perfectly fine with a manual mount that does not have Goto, or even with a Goto Mount where you have other means to move the mount (e.g. handset, manual slewing).  If you have a mount that isn't listed below or are just starting with Astrid, it may be best to get familiar with Astrid slewing your mount manually prior to setting up Goto.

Manual mounts in Astrid use a simulated mount to maintain the internal pointing model for Astrid.  Astrid installed example simulated mounts when it was built and a few other common mounts.

## Mounts and Connections Supported

Astrid includes [IndiLib](indilib.org) for mount support, and any mount that is supported by [IndiLib](indilib.org) will also likely work with Astrid when configured correctly. The mount must support a Serial connection over USB to work with Astrid.  Wifi/Bluetooth connections to mounts are not supported with Astrid due to the Wifi already being used for Astrid's Hotspot and connection to your Home network and then the general unreliability of connections to mounts over Wifi and Bluetooth.

Often, there are multiple methods for connecting to a mount from USB to serial, and which is the best depends on your mount.  Generally, a direct serial connection is simpler and often doesn't require star alignment on a handset prior to use (as Astrid can tell the mount where it is in the sky).  A mount that has a handset (e.g. Synscan) often has the ability for a direct-to-mount connection (Synscan removed), and also a connection via a handset (pass-thru) and also a connection via a handset (synscan protocol).

Often, you may need to purchase a cable for the serial connection. Information on which cable you need can often be found from the manufacturer (maybe in your mount manual), [Cloudy Nights](https://www.cloudynights.com) or the [IndiLib Forum](https://indilib.org/forum.html) typically.

Check the list below and use it as a starting point for mount configuration.  The list contains mounts that have been tested by others and are known to work.  

**If you've got your mount working and it's not listed below, please send the settings/configuration that you found to work so it can be added to the list and others can benefit.**

If you have a common commercial mount, it's more likely to be supported than a unique or rare large observatory mount or a boutique expensive mount that few others have.  However, occasionally, you can be lucky and have unique mounts that support, say, the LX200 protocol or EQMOD/EQDIR and are likely to work.

Most commercial mounts work in JNOW coordinates, and Astrid should be configured as such. Occasionally, though, a mount may be J2000.

Alt-Az mounts, in particular, contain an internal pointing model that must be set up on mount startup. Often, handsets have a 1, 2, or 3-star alignment process to do this and require the time, date, and location to be entered before they will talk over serial. If you can connect directly to the mount without the handset, you can often skip this lengthy process, and Astrid will set up the mount alignment for you.

You should make sure that your mount (and handset's) firmware is updated to the latest version.  Before configuring any new mount, it is advisable to ascertain the exact make and model of the mount and find out specific information about cables or configuration details you may need from [IndiLib - Telescopes](https://indilib.org/devices/mounts.html). Clicking on on the image for the mount will take you to a page with further details.  Information you will need, for example, are the Driver Executable, Connectivity, and Issues.

Some mounts (and handsets) will look like they are working when they are powered over USB. Always make sure the main power is connected to the mount.

Most of the mount functionality can be tested during daylight if you line up the mount with North and treat alignment stars as they would be in their correct locations for the time of day.  A final test can then be left till a clear night.

## Support

Limited support is available over Zoom if you have purchased an Astrid through approved channels, such as IOTA (North America), IOTA/ES, or directly from the Author.

Any requests for support need to have the exact make, model and configuration (Alt/Az or Eq) of the mount and a link to the operation manual.

Prior to requesting support, please ensure:

1. You have checked the list below for your mount, the documentation here, and tried setting it up
2. On your desktop computer you have:
	
	* Zoom Installed
	* RealVNC installed and talking to Astrid
	* Mount connected to Astrid with the correct cable and powered on
3. 

	It's then possible to setup a zoom session with screen sharing to assist you.
	



## Mount Settings

Settings for mounts can be accessed via Astrid's settings "Mount" panel.  Display Name can be anything, but please keep it short so it fits on the display.  Local Timezone Offset should always be 0.00.

| Mount/Model | Tested | Indi Module | Indi Telescope Id | Indi Custom Properties | Indi USB tty | Baud Rate | Mount Alignment Type | Goto Capability | Tracking Capability | Mount is J2000 | Parking Method | Cable | Notes |
| ----------- | ------ | ----------- | ----------------- | ---------------------- | ------------ | --------- | -------------------- | --------------- | ------------------- | -------------- | -------------- | ----- | ----- |
Fixed Manual Mounts or Incompatible Goto Mounts (uses Astrid Prepoint) | Yes | indi\_simulator\_telescope | <code>Telescope Simulator</code> | | /dev/ttyUSB0 | 9600 | altaz | unchecked | unchecked | unchecked | park | None | <code>This is a simulated mount and the default for prepoint, manual mounts, scopes without Goto or Goto mounts where communication isn't supported.</code> |
| Celestron Nexstar 6SE/8SE | Yes | indi\_celestron\_aux | <code>Celestron AUX</code> | <code>Celestron AUX.PORT_TYPE.PORT\_HC\_USB=On;Celestron AUX.CORDWRAP.INDI\_ENABLED=On</code> | /dev/ttyUSB0 | 19200 | altaz | checked | checked | unchecked | park | | <code>IMPORTANT: Power to the mount must be on.  The handset will show text even when not powered as it can get power via the USB, but the mount won't connect. LCD will have red backlight when power to the mount is on.  Mount must be powered on horizontal pointing North. Occasionally when started, mount may need "Try Again" on startup. Nexstar tracking is terrible, it's suggested to use the SE6/SE8 for prepoint goto.  Do not do any star alignment prior to (or after) connecting the mount, it's not required as this bypasses the regular mount firmware.</code> |
| EQMod Mounts (Other) | No | indi\_eqmod\_telescope | <code>EQMod Mount</code> | | /dev/ttyUSB0 | 115200 | eq | checked | checked | unchecked | park | USB Cable | <code>Unplug Synscan</code> |
| Losmandy Gemini 2 | Yes | indi\_lx200gemini | <code>Losmady Gemini</code> | | /dev/ttyACM0 | 9600 | eq | checked | checked | unchecked | park | | Regular A/B USB  <code>See Steve Preston</code> |
| LX200 Classic | Yes | indi\_lx200classic | <code>LX200 Classic</code> | | /dev/ttyUSB0 | 9600 | altaz (should work in eq too) | checked | checked | unchecked | park | [Clearline](https://www.clearline-tech.com/repair-parts/lx200/lx200-usb-adapter.html) | <code>Tracking is permanently on with this mount.</code> |
| Skywatcher AZ EQ5, Skywatcher AZ EQM-35 Pro| Yes | indi\_eqmod\_telescope | <code>EQMod Mount</code> | | /dev/ttyUSB0 | 115200 | eq | checked | checked | unchecked | park | USB Cable | <code>Unplug Synscan</code> |
| Skywatcher AZ (example: Skywatcher Virtuoso GTI 150p (tested), FlexTube 300P(tested), FlexTube 350p, FlexTube 400P) | Yes | indi\_skywatcherAltAzMount | <code>Skywatcher Alt–Az</code> | | /dev/ttyUSB0 | 9600 | altaz | checked | checked | unchecked | park | [RJ12 Control Cable for Skywatcher Az-GTI and AZ-GTE](https://www.amazon.com/gp/product/B08DG7KKNV) | <code>Power mount on with tube horizontal and pointing north (the park position).  Use EqMod Cable. The EqMod cable must be plugged into the same place the handset plugs into (i.e. instead of the handset) on the mount.  On startup, Astrid may say "Failed to connect to mount", just click "Try Again".</code> |
| Vixen Starbook Ten | Yes | indi\_starbook\_ten | <code>Starbook Ten</code> | | /dev/null | 9600 | eq | checked | checked | unchecked | park | ethernet | <code>Connect to ethernet port on Pi. Point Dec West at startup (home position), accept warning about sun, then connect Astrid. Note Park on Starbook Ten often means RA is rotated, it is okay to start a polar alignment from this position.</code> |
| ZWO AM5 (likely AM3/AM5N too) | Yes | indi\_lx200am5 | <code>ZWO AM5</code> | | /dev/tty/ACM0 | 9600 | eq | checked | checked | unchecked | home | Regular A/B USB | |

*Author only: OPTION-SPACE for non-breaking space above*

## Mount Testing and Verification

Mounts that haven't been encountered before with Astrid (i.e., there are no settings listed above) need to be verified to work on Astrid.  This process details how to do that:

* Indi Module must be set to the correct module.  A list of modules can be determined from the command line by <code>ls /usr/bin/indi*</code>  Also use [IndiLib - Telescopes](https://indilib.org/devices/mounts.html) to determine the correct module for your mount.  Save settings, quit astrid and restart Astrid
* Type <code>indi\_getprop</code> in the command line to determine the value for <code>DRIVER\_INFO.DRIVER_NAME</code> and enter that into "Indi Telescope Id" and restart Astrid. Note if you see "connect: Connection refused", then you didn't start Astrid and didn't click on "Start Astrid"
* If you have connection issues, use indi\_getprop to check that CONNECTION.CONNECT is On and indi\_setprop to set it, you may need to change some of the settings to get a connection.
* Check UTC is set correctly on the mount (using indi\_getprop) to the time you started Astrid (note it generally doesn't update whilst it's running)
* Check Latitude and Longitude for the site are correct (using indi\_getprop) after Update Site has been clicked in Astrid
* Does Goto work?
* Does Home/Park work?
* Does Tracking stop and start when the Tracking button is toggled?
* Does Tracking come back on automatically after a Goto?
* Does the mount update it's position correctly after a Sync is done after a plate solve?
* Does the STOP button (in the mount panel), stop the mount motion during Park/Homing and a Goto?
* Does the Tracking Rate (sidereal, lunar etc.) remain after Gotos?
* Do the Slew Joystick buttons and slew rate work?
* Does Meridian Flip work? (find star close to meridian (South), goto, wait for Meridian timing to drop to -1m, goto again and check mount flips.
* Does the Polar Align routine work (test this at night and german equatorial mounts only).

**If you've got your mount working and it's not listed below, please send the settings/configuration that you found to work so it can be added to the list and others can benefit.**
