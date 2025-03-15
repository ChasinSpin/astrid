# Focusers (Electronic)

* [Introduction](#introduction)
* [Focusers and Connections Supported](#focusers-and-connections-supported)
* [Support](#support)
* [Focuser Settings](#focsuer-settings)
* [Focuser Testing And Verification](#focuser-testing-and-verification)

## Introduction

Connecting your Focuser to Astrid may take some effort, especially if no one has set up the same or similar focuser before. Many different focuser manufacturers and focuser models exist, and they lack consistency in operation, features, and requirements between them.

Astrid also does not require a Focuser and works perfectly fine with a manual Focuser. Astrid defaults to a simulated focuser unless you change it.

## Focuser and Connections Supported

Astrid includes [IndiLib](indilib.org) for focuser support, and any focuser that is supported by [IndiLib](indilib.org) will also likely work with Astrid when configured correctly. The focsuer must support a USB connection to work with Astrid.  Wifi/Bluetooth connections to focusers are not supported with Astrid.

Check the list below and use it as a starting point for focuser configuration.  The list contains focusers that have been tested by others and are known to work.  

**If you've got your focuser working and it's not listed below, please send the settings/configuration that you found to work so it can be added to the list and others can benefit.**

You should make sure that your focuser firmware is updated to the latest version.  Before configuring any new focuser, it is advisable to ascertain the exact make and model of the focuser and find out specific information about cables or configuration details you may need from [IndiLib - Telescopes](https://indilib.org/devices/focusers.html). Clicking on on the image for the mount will take you to a page with further details.  Information you will need, for example, are the Driver Executable, Connectivity, and Issues.

The focuser functionality can be tested during daylight.

## Support

Limited support is available over Zoom if you have purchased an Astrid through approved channels, such as IOTA (North America), IOTA/ES, or directly from the Author.

Any requests for support need to have the exact make, model of the focuser and a link to the operation manual.

Prior to requesting support, please ensure:

1. You have checked the list below for your focuser, the documentation here, and tried setting it up
2. On your desktop computer you have:
	
	* Zoom Installed
	* RealVNC installed and talking to Astrid
	* Mount connected to Astrid with the correct cable and powered on
3. It's then possible to setup a zoom session with screen sharing to assist you.
	



## Focuser Settings

Settings for focusers can be accessed via Astrid's settings "Focus" panel.  

| Focuser/Model | Tested | Indi Module | Indi Telescope Id | Indi Custom Properties | Cable | Notes |
| ------------- | ------ | ----------- | ----------------- | ---------------------- | ----- | ----- |
| Simulated Focuser | Yes | indi\_simulator\_focuser | <code>Focuser Simulator</code> | | <code>This is a simulated focuser and the default.</code> |
| ZWO EAF | Yes | indi\_asi\_focuser | <code>ASI EAF</code> | <code>ASI EAF.FOCUS\_REVERSE\_MOTION.INDI\_DISABLED=On or ASI EAF.FOCUS\_REVERSE\_MOTION.INDI\_ENABLED=On</code>

*Author only: OPTION-SPACE for non-breaking space above*

### Reversing The Direction Of the Focuser

Try adding the following in "Indi Custom Properties":

> ASI EAF.FOCUS\_REVERSE\_MOTION.INDI\_DISABLED=On

OR

> ASI EAF.FOCUS\_REVERSE\_MOTION.INDI\_DISABLED=Off

Where ASI EAF is the Indi Focuser Device Id.

## Focuser Testing and Verification

Focusers that haven't been encountered before with Astrid (i.e., there are no settings listed above) need to be verified to work on Astrid.  This process details how to do that:

* Indi Module must be set to the correct module.  A list of modules can be determined from the command line by <code>ls /usr/bin/indi*</code>  Also use [IndiLib - Telescopes](https://indilib.org/devices/focusers.html) to determine the correct module for your focuser.  Save settings, quit astrid and restart Astrid
* Type <code>indi\_getprop</code> in the command line to determine the value for <code>DRIVER\_INFO.DRIVER_NAME</code> and enter that into "Indi Focuser Device Id" and restart Astrid. Note if you see "connect: Connection refused", then you didn't start Astrid and didn't click on "Start Astrid"
* If you have connection issues, use indi\_getprop to check that CONNECTION.CONNECT is On and indi\_setprop to set it, you may need to change some of the settings to get a connection.
* Does Set Position work?
* Does Set Current Position Work?
* Do the Up/Down arrows work
* Does Stop Movement Work

**If you've got your focuser working and it's not listed below, please send the settings/configuration that you found to work so it can be added to the list and others can benefit.**
