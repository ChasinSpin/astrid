# Mounts

## Mounts

##### Probably should link to mount.json configurations here

| Model | Tested | Notes |
| ----- | ------ | ----- |
| ZWO AM5 | Yes | /dev/ttyACM0, 9600, parkmethod=home |
| Skywatcher AZ EQ5 | Yes | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| Skywatcher AZ EQM-35 Pro | Yes | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| EQMOD Mounts | Most Should Work | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| Losmandy Gemini 2 | Yes | /dev/ttyACM0, 9600, parkmethod=park, Indi Telescope Device Id=Losmandy Gemini, Indi Module=indi_lx200gemini |
| Vixen Starbook Ten | Yes | Connect to ethernet port on the Pi. Point Dec West at start up (home position), accept warning about sun, then connect Astrid.  Note Park on Starbook Ten often means RA is rotated, it is okay to start a polar alignment from this position. |
| LX200 Classic | Yes | /dev/ttyUSB0, 9600, parkmethod=park, Indi Telescope Device Id=LX200 Classic, Indi Module = indi_lx200classic   Tested in AltAz, should work in Equatorial.  Tracking is permanently on with this mount. Connect via USB to the mount directly with this: https://www.clearline-tech.com/repair-parts/lx200/lx200-usb-adapter.html |
| Skywatcher AZ GTI | Yes | /dev/ttyUSB0, parkmethod=park, Indi Telescope Device Id = Skywatcher Alt-Az, Indi Module=indi_skywatcherAltAzMount   Alt Az mount, baud=9600, example Skywatcher Virtuoso GTI 150p.  Power mount on with tube horizontal and pointing north (the park position). Use EQMod Cable. Regularly on startup, says "Failed to connect to mount", just click Try Again |
| Celestron Nexstar 6 SE (likely 8 SE too and other celestron mounts) | Yes |  /dev/ttyUSB0, parkmethod=park, Indi Telescope Device Id=Celestron AUX, Indi Module=indi_celestron_aux, baud=19200, Indi Custom Properties=Celestron AUX.PORT_TYPE.PORT\_HC\_USB=On;Celestron AUX.CORDWRAP.INDI\_ENABLED=On   (note "Celestron AUX" has a space in it. Note: USB connection via the handset (USB-A to USB-Mini B) is tested, also connection via the AUX port may work but will require settings changes.  IMPORTANT: Power to the mount must be on.  The handset will show text even when not powered as it can get power via the USB, but the mount won't connect. LCD will have red backlight when power to the mount is on.  Mount must be powered on horizontal pointing North. Occasionally when started, mount may need "Try Again" on startup. Nexstar tracking is terrible, it's suggested to use the SE6/SE8 for prepoint goto.  Do not do any star alignment prior to (or after) connecting the mount, it's not required as this bypasses the regular mount firmware. |
| Fixed Mounts (Prepoint) | Yes | Use Simulator |

### Mount Onboarding/Testing/Verification

* Verify connection/communication (indi\_getprop / indi\_setprop)
* CONNECT = On ?
* UTC Set?
* Lat/Lon set
* Goto work?
* Home/Park work?
* Tracking Toggle working?
* Tracking coming on automatically after Slew?
* Sync working after plate solve?
* Abort Motion working?
* Check Tracking Rate changes are stored (sidereal, lunar etc.)
* Check Manual Slew and Speeds work
* Meridian flip working (find star close to meridian (South), goto, wait for Meridian timing to drop to -1m, goto again and check mount flips.
* Check Polar Align routine works (GEM mounts only)
