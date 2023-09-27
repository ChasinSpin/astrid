# Mounts

## Mounts

##### Probably should link to mount.json configurations here

| Model | Tested | Notes |
| ----- | ------ | ----- |
| ZWO AM5 | Yes | /dev/ttyACM0, 9600, parkmethod=home |
| Skywatcher AZ EQ5 | Yes | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| Skywatcher AZ EQM-35 Pro | Yes | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| EQMOD Mounts | Most Should Work | /dev/ttyUSB0, 115200, parkmethod=park, Connect via USB to the mount directly (unplug SynScan) |
| Losmandy Gemini 2 | In Progress | /dev/ttyACM0, 9600|
| Vixen Starbook Ten | Yes | Connect to ethernet port on the Pi. Point Dec West at start up (home position), accept warning about sun, then connect Astrid.  Note Park on Starbook Ten often means RA is rotated, it is okay to start a polar alignment from this position. |
| Fixed Mounts (Prepoint) | Yes | Use Simulator |

### Mounts we don't recommended

* Celestron Nexstar 6 SE (likely 8 SE too). Dec/RA vary whilst running causing some short exposures to be trailed randomly. Mount can't be updated for Time and Location after the scope is aligned).  Star alignment on the handset should work but didn't during testing (the scope could have been faulty).  If attempting to use, then you will need to align the scope prior to connecting with ASTRID, and you will need to set the time and location exactly from the handset.  Also, RA/DEC was often reported incorrectly.

		"name": "NexStar SE",
		"indi_module": "indi_celestron_gps",
		"indi_telescope_device_id": "Celestron GPS",
		"indi_usb_tty": "/dev/ttyUSB0",
		"mount_needs_slew_state": false,
		"mount_is_j2000": false,
		"local_offset": "0.00"


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

