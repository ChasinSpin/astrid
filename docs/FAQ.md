# FAQ

* [Power Jack Is Intermittent](#power-jack-is-intermittent)
* [Cleaning the Astrid 3D printed case](#cleaning-the-astrid-3D-printed-case)
* [I have multiple Astrids, do I need a computer for each one?](#i-have-multiple-astrids-do-i-need-a-computer-for-each-one)
* [What's the best device to control Astrid?](#whats-the-best-device-to-control-astrid)
* [Unattended setups, do I need to leave my tablet/computer/phone?](#unattended-setups-do-i-need-to-leave-my-tabletcomputerphone)
* [Is Astrid for Prepoint only?](#is-astrid-for-prepoint-only)
* [Which video analysis software is supported?](#which-video-analysis-software-is-supported)
* [Which light curve analysis software is supported?](#which-light-curve-analysis-software-is-supported)
* [Astrid, Hot Climates, Cold Weather, and moisture](#astrid-hot-climates-cold-weather-and-moisture)
* [Stealth Mode - removing lights for unattended operation](#stealth-mode-\--removing-lights-for-unattended-operation)
* [Stretching (display)](#stretching-display)
* [Plate Solving Arrows On Manual Equatorial Mounts](#plate-solving-arrows-on-manual-equatorial-mounts)
* [Star/Planet/Moon Saturates At Highest Video Frame Rate](#starplanetmoon-saturates-at-highest-video-frame-rate)
* [Optical Train Dimensions and BackFocus Distance](#optical-train-dimensions-and-backfocus-distance)
* [Does Astrid Require Internet](#does-astrid-require-internet)
* [Which Version is Astrid](#which-version-is-astrid)
* [Failed Upgrades](#failed-upgrades)
* [Copying the USB Drive](#copying-the-usb-drive)

### Power Jack Is Intermittent

If the power jack is intermittent, then please push the plug fully into the jack.  Astrid's power jacks are high-power, high-grade power jacks designed for long life (unlike many astro devices).  To enagage the jack fully, it needs to be fully pushed in which may take some pressure, especially when new.

### Cleaning the Astrid 3D printed case

There are 2 types of cases that ship with Astrid, the older Resin Case, and the newer FDM printed ASA case.
	
For the Resin case ONLY, use Acetone to remove marks the case, be careful to to touch anything with the acetone which is not the resin case as it will melt plastics.
	
For the FDM printed case, clean it damp cloth or a bit of Isopropyl Alcohol.
	
The case should only be cleaned with power off, being careful not to use access solution that will get into the device.

### I have multiple Astrids, do I need a computer for each one?

Only one computer/tablet or phone is needed to control all Astrids

### Do I need an Astrid Mini Display for every Astrid?

No, you only need one for all the Astrids you own, it can be unplugged and moved to another Astrid
	
### What's the best device to control Astrid?
	
A tablet that can run VNC (e.g. iPad) is the most convenient to control Astrid as it's very portable and a reasonably large screen.  However a phone could be used (smaller screen) or computer (larger screen but more bulky)
	
### Unattended setups, do I need to leave my tablet/computer/phone?

No, Astrid will keep runing despite you not being connected to it, take your tablet/computer/phone with you.
	
### Is Astrid for Prepoint only?

Astrid can be used with Goto scopes too, any scope supported by Indilib is supported by Astrid
	
### Which video analysis software is supported?
	
Currently, only Bob Anderson's PyMovie has support to read the RAVF video files that Astrid generates. Astrid does not generate ADV format files due to the lack of 10-bit RAW support. Astrid player can convert to FITs files, but you will lose audit information that Astrid generates and that conversion would take a long time. Limovie and Tangra do not support RAVF at this time, if you wish to see Astrid run with these applications, please contact their authors to request. Once the light curve has been extracted by PyMovie, it can be read in PyOTE, AOTA, ROTE or Occular.
	
### Which light curve analysis software is supported?

Once the light curve has been generated in PyMovie, it can be analyzed in PyOTE, AOTA, ROTE or Occular.

### Astrid, Hot Climates, Cold Weather, and moisture

Astrid normally runs above ambient temperature, so generally inside the case little moisture or ice will accumulate.  However if the temperature outside is substantially below freezing, to the point that condensation would form on the case when brought inside, then it is advisable to place in a container until warmed to room temperature and then open the container to remove any remaining moisture.  This would be the same treatment you would apply to a telescope.

Astrid is not waterproof and shouldn't be subjected to rain or snow. Also, it's not weatherproof, so don't leave it outside permanently, as is the same with most astronomical equipment.

One user loosely covers Astrid on top with a plastic bag leaving space for venting if they have concerns about rain overnight.  Astrid does generate heat, and it's advisable not to completely enclose it to avoid overheating.

Also, Astrid is subjected to Canadian weather and so far has been tested to -30C with no issues encountered to date.
	
In hot climates, make sure you have adequate venting around Astrid.
	
### Stealth Mode - removing lights for unattended operation

Astrid has a number of leds on it that may blink or glow, they are made available so that the status of the device can be seen:
	
* GPS LED (red flashing once per second with GPS fix)
* Raspberry Pi: Red LED (power) and Green LED (activity)
* Network Status LEDs (Green and Yellow, flashing or static)

To use Astrid stealthily, just cover these LEDs with electrical tape on the case. (the GPS LED can be accessed by unbolting the case where the Astrid Logo is, and covering the LED on the GPS board with electrical tape).  Scotch Super 33+ is a suggested electrical tape.
	
Additionally, the Raspberry Pi Red/Green LEDs and Network Status LEDs can be switched off from software via the "Light Out" tool in Astrid Tools on the desktop.
	
### Stretching (display)

Astrid has built-in stretching with 3 different methods. Astrid never stretches the data it saves, which is always saved in raw format.  Stretching is only to make stars easier to see on the display.

*CLAHE (Contrast Limited Adaptive Histogram Equalization* - This can be thought of as an auto-stretch and is Astrid's default. It will automatically adjust and can handle thin clouds, light pollution, smoke, different exposure settings, and glow due to the sun near sunrise and sunset. High values of CLAHE can look soft sometimes, so experiment with the varies settings provided.
	
*Histogram Equalization* - This is a method that adjusts the contrast using histogram equalization so the image is more uniformly distributed across the entire range of values. We have found it to perform a little less well than CLAHE, but your mileage may vary.
	
*Min Max* - This manual method evenly distributes the image between Min and Max.  Values below Min will be black, and values over Max with be White, with everything between distributed evenly as levels of gray.  Min and Max are between 0 and 255 with Min being less than Max.  Some Min/Max values are predefined for your convenience, but adjusting them using "Custom" is often required.  Although Min/Max gives you superior control over stretch, if conditions change (clouds, smoke, light pollution, sun, exposure), you will likely need to change your Min/Max values.
	
### Plate Solving Arrows On Manual Equatorial Mounts	
When Astrid Plate solves, it provides arrows telling the user where to move the telescope. If the scope has Goto, the scope can then move automatically to the location of the target, but if it's a manual scope, the user needs to slew the scope.  Depending on the users' preference, The plate solver can print 2 direction arrows (Altitude and Azimuth) or 1 arrow (overall direction).
	
With Alt/Az mounts, it's simple: Move the mount in the direction of the arrows using the scope's Altitude and Azimuth adjustments.

For Equatorial mounts, the user needs to think in terms of where the scope is visually pointing and make RA/Dec adjustments to slew the scope to the desired location.  Another way to think about this is that it's the same process you would use with an Equatorial mount if you were star hopping from a chart.  You would look at the chart and say I need to go from this star to that star and I need to go up and right and make the RA/Dec adjustments and combine them were necessary to get there.
	
### Star/Planet/Moon Saturates At Highest Video Frame Rate

Occasionally, if the telescope is very large, or stars are bright, the Astrid sensor may saturate at the highest frame rate.  The first method to reduce the brightness is to reduce the gain.  If it is still saturating after that and you need to reduce the brightness further, then use a Neutral Density (ND) filter. ND filters for 1.25" are cost-effective and screw into the barrel of the IOTA 0.5X reducer.

### Optical Train Dimensions and BackFocus Distance

For the optical train dimensions for calculating backfocus, or for ordering the correct adapter to work with a Hyperstar, see the following:

![IOTA Astrid Back Focus and Adapter Dimensions 1.25" Barrel](images/BackFocus1.png)

Note: To reduce the focal length further, spacer rings (e.g. 5mm) can be added between the focal reducer and the IOTA C/CS Mount to 1.25" F adapter. A typical SCT can benefit from 3 x 5mm spacer rings and still have focusing range.

An alternative, if you don't require the focal reducer is a straight C/CS Mount to 1.25" Barrel Connector [SVBONY C Mount to 1.25" Video Camera Barrel Adapter](https://www.amazon.com/gp/product/B07R4SSBKC) 

![Alternative Back Focus and Adapter Dimensions M48F or M42F/T2](images/BackFocus2.png)

* A: [Metal M42 to M48 Male to Female Step-Up Coupling Ring Adapter](www.amazon.com/dp/B081382KJV)
* B: [C Mount(25mm 0.75mm Pitch) to T T2 (42mm 0.75mm Pitch) Coupling Ring Adapter](www.amazon.com/dp/B0813129HJ)

### Does Astrid Require Internet

Astrid requires the internet for a few features, but it is designed for fully autonomous mobile use without internet.  It can be used where there is no cellular or wifi signal.

Internet is not required for:

* Plate Solving:
    Ted ships the majority if not all of the Plate Solve catalogs on the USB drive, so an internet connection is not required, all plate solves occur with local data from the USB drive and are offline.  If you are setting up a new scope and have deleted unused plate solve files, Astrid will prompt and download for the missing files when starting up when connected to the internet if the correct focal length has been entered in the settings. Plan to roughly configure any new scopes where you have internet.
* Objects (except SIMBAD)
* Occultation Events
* Prepoints

Internet is required for:

* Occasionally once every 3 months to download the latest IERs data for earths' rotation (this happens automatically when connected to the internet)
* Syncing events with OWCloud
* Looking up SIMBAD objects (but you can then save those to the Custom database that is offline)
* Software Upgrades

General advice is to connect to the internet before you leave home and:

1. Do a software upgrade if necessary
2. Sync your stations from OWCloud
3. Download any astro targets you may want to do photography of via SIMBAD and save to Custom (doesn't apply to occultation events)
4. Shutdown
5. Setup at your deployment location (with or without internet)

### Which Version Is Astrid

Astrid's version is displayed on startup on the splash screen.  If you wish to find the version when Astrid is running, or without running Astrid, you can start a Terminal and type:   cat ~/astrid/version.txt

To find the number of the latest version: [Github Astrid Version](https://github.com/ChasinSpin/astrid/blob/main/version.txt)

Astrid will check when started *when internet is connected* to see if it needs an upgrade and prompts you.

### Failed Upgrades

If an upgrade fails (often due to internet connectivity), then just repeat the upgrade.

IMPORTANT: If an upgrade fails and you afe unable to fix by repeating, it's is strongly recommended that you don't reformat the USB Thumb Drive and reimage the SD Card, it will likely make matters worse.  Please reach out for support instead.

### Copying the USB Drive

To copy the USB Drive (for example to backup or as a spare):

* Run the "Format USB Flash Drive" utility in the Tools folder on the Astrid Desktop to format the new drive
* Insert the original USB Drive into your Windows or Mac desktop/laptop and copy the files onto your desktop
* Eject the original USB Drive
* Insert the new USB Drive into your Windows or Mac desktop/laptop and copy the files you previously copied from your desktop onto your new USB Drive, overwriting the files the format created
* Eject the original USB Drive

ALWAYS format your new USB Drive using the Astrid utility otherwise Astrid will not recognize the drive.