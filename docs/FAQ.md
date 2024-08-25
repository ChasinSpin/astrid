# FAQ

* [Cleaning the Astrid 3D printed case](#cleaning-the-astrid-3D-printed-case)
* [I have multiple Astrids, do I need a computer for each one](#i-have-multiple-astrids,-do-i-need-a-computer-for-each-one)
* [What's the best device to control Astrid](#what's-the-best-device-to-control-astrid)
* [Unattended setups, do I need to leave my tablet/computer/phone](#unattended-setups,-do-i-need-to-leave-my-tablet/computer/phone)
* [Is Astrid for Prepoint only](#is-astrid-for-prepoint-only)
* [Which video analysis software is supported](#which-video-analysis-software-is-supported)
* [Which light curve analysis software is supported](#which-light-curve-analysis-software-is-supported)
* [Astrid, Hot Climates, Cold Weather, and moisture](#astrid,-hot-climates,-cold-weather,-and-moisture)
* [Stealth Mode - removing lights for unattended operation](#stealth-mode---removing-lights-for-unattended-operation)
* [Stretching (display)](#stretching-(display))
* [Plate Solving Arrows On Manual Equatorial Mounts](#plate-solving-arrows-on-manual-equatorial-mounts)
* [Star/Planet/Moon Saturates At Highest Video Frame Rate](#star/planet/moon-saturates-at-highest-video-frame-rate)

### Cleaning the Astrid 3D printed case

There are 2 types of cases that ship with Astrid, the older Resin Case, and the newer FDM printed ASA case.
	
For the Resin case ONLY, use Acetone to remove marks the case, be careful to to touch anything with the acetone which is not the resin case as it will melt plastics.
	
For the FDM printed case, clean it damp cloth or a bit of Isopropyl Alcohol.
	
The case should only be cleaned with power off, being careful not to use access solution that will get into the device.

### I have multiple Astrids, do I need a computer for each one

Only one computer/tablet or phone is needed to control all Astrids

### Do I need an Astrid Mini Display for every Astrid

No, you only need one for all the Astrids you own, it can be unplugged and moved to another Astrid
	
### What's the best device to control Astrid
	
A tablet that can run VNC (e.g. iPad) is the most convenient to control Astrid as it's very portable and a reasonably large screen.  However a phone could be used (smaller screen) or computer (larger screen but more bulky)
	
### Unattended setups, do I need to leave my tablet/computer/phone

No, Astrid will keep runing despite you not being connected to it, take your tablet/computer/phone with you.
	
### Is Astrid for Prepoint only

Astrid can be used with Goto scopes too, any scope supported by Indilib is supported by Astrid
	
### Which video analysis software is supported
	
Currently, only Bob Anderson's PyMovie has support to read the RAVF video files that Astrid generates. Astrid does not generate ADV format files due to the lack of 10-bit RAW support. Astrid player can convert to FITs files, but you will lose audit information that Astrid generates and that conversion would take a long time. Limovie and Tangra do not support RAVF at this time, if you wish to see Astrid run with these applications, please contact their authors to request. Once the light curve has been extracted by PyMovie, it can be read in PyOTE, AOTA, ROTE or Occular.
	
### Which light curve analysis software is supported

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