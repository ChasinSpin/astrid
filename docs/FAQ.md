# FAQ

* **Cleaning the Astrid 3D printed case**

	Use Acetone to remove marks the case, be careful to to touch anything with the acetone which is not the resin case as it will melt plastics.

* **I have multiple Astrids, do I need a computer for each one?**

	Only one computer/tablet or phone is needed to control all Astrids

* **Do I need an Astrid Mini Display for every Astrid?**

	No, you only need one for all the Astrids you own, it can be unplugged and moved to another Astrid
	
* **Whats the best device to control Astrid?**
	
	A tablet that can run VNC (e.g. iPad) is the most convenient to control Astrid as it's very portable and a reasonably large screen.  However a phone could be used (smaller screen) or computer (larger screen but more bulky)
	
* **Unattended setups, do I need to leave my tablet/computer/phone**

	No, Astrid will keep runing despite you not being connected to it, take your tablet/computer/phone with you.
	
* **Is Astrid for Prepoint only?**

	Astrid can be used with Goto scopes too, any scope supported by Indilib is supported by Astrid
	
* **Which video analysis software is supported?**
	
	Currently, only Bob Anderson's PyMovie has support to read the RAVF video files that Astrid generates. Astrid does not generate ADV format files due to the lack of 10-bit RAW support. Astrid player can convert to FITs files, but you will lose audit information that Astrid generates and that conversion would take a long time. Limovie and Tangra do not support RAVF at this time. Once the light curve has been extracted by PyMovie, it can be read in PyOTE, AOTA, ROTE or Occular.
	
* **Which light curve analysis software is supported?**

	Once the light curve has been generated in PyMovie, it can be analyzed in PyOTE, AOTA, ROTE or Occular.

* **Astrid, Hot Climates, Cold Weather, and moisture**

	Astrid normally runs above ambient temperature, so generally inside the case little moisture or ice will accumulate.  However if the temperature outside is substantially below freezing, to the point that condensation would form on the case when brought inside, then it is advisable to place in a container until warmed to room temperature and then open the container to remove any remaining moisture.  This would be the same treatment you would apply to a telescope.

	Astrid is not waterproof and shouldn't be subjected to rain or snow. Also, it's not weatherproof, so don't leave it outside permanently, as is the same with most astronomical equipment.

	One user loosely covers Astrid on top with a plastic bag leaving space for venting if they have concerns about rain overnight.  Astrid does generate heat, and it's advisable not to completely enclose it to avoid overheating.

	Also, Astrid is subjected to Canadian weather and so far has been tested to -30C with no issues encountered to date.
	
	In hot climates, make sure you have adequate venting around Astrid.
	
* **Stealth Mode - removing lights for unattended operation**

	Astrid has a number of leds on it that may blink or glow, they are made available so that the status of the device can be seen:
	
	* GPS LED (red flashing once per second with GPS fix)
	* Raspberry Pi: Red LED (power) and Green LED (activity)
	* Network Status LEDs (Green and Yellow, flashing or static)

	To use Astrid stealthily, just cover these LEDs with electrical tape on the case. (the GPS LED can be accessed by unbolting the case where the Astrid Logo is, and covering the LED on the GPS board with electrical tape).  Scotch Super 33+ is a suggested electrical tape.
	