# Usage Guide

* [Power](#power)
* [Startup](#startup)
* [Windows Zeroconf](#windows-zeroconf)
* [Connectivity WiFi and Hotspot](#connectivity-wifi-and-hotspot)
* [First Light](#first-light)
* [Connect Via VNC](#connect-via-vnc)
* [Internet Access](#internet-access)
* [Upgrade](#upgrades)
* [Focal Reducers And Length](#focal-reducers-and-length)
* [Multiple Astrids](#multiple-astrids)
* [Our Setup](#our-setup)
* [SSH And SFTP](#ssh-and-sftp)
* [Prepointing](#prepointing)
* [Auto Record and OWCloud](#auto-record-and-owcloud)
* [Player](#player)
* [Light Curve Analysis](#light-curve-analysis)
* [Occult4 Searches](#occult4-searches)

## Power

Good power is critical to Astrid. Please see [Power Supply](PowerSupply.md) for more information.

## Startup

* Insert microSD Card into ASTRID.  Note the contacts on the card face towards the logo on ASTRID.  Be careful to insert it into the socket (*not beside it*).
* Insert USB Flash drive **in BLUE USB port (USB 3.1)** on ASTRID.  Note the black USB ports are slower USB 2.0.
* Connect GPS Antenna (ensure it has a clear view of the sky, see [Troubleshooting](Troubleshooting.md) for GPS Poor Reception for more information.
* Connect mount if using to any remaining USB port.
* Connect [Astrid Mini Display](MiniDisplay.md) to any remaining USB port.
* Power mount on.
* Power ASTRID on.
* **ALWAYS REMEMBER TO SHUTDOWN ASTRID AND WAIT 15 SECONDS AFTER GREEN LIGHT STOPS FLASHING ON THE SIDE BEFORE REMOVING POWER TO AVOID SD CARD AND USB FLASH DRIVE CORRUPTION.**
* Keep sensor clean.  The best way to do this is to use a camera puffer and keep the sensor covered at all times, either with a cap or a focal reducer.  If you need to clean the sensor, use a regular sensor cleaning kit.  As with regular astrophotography, a dirty sensor is indicated by sharply focused defects on the image (*less defined defects are dirt on the lens or telescope*).
* [Connect via VNC](#connect-via-vnc)

## mDns/Bonjour/Windows Zeroconf

**Note: This is important for older versions of Android/Windows Tablets and Windows Computers**

Zeroconf (also known as mDNS and Bonjour) is a way to save users from entering IP addresses (e.g. 10.0.0.5) and being able to use name.local instead: [https://en.wikipedia.org/wiki/Zero-configuration_networking
](https://en.wikipedia.org/wiki/Zero-configuration_networking)

Ordinarily, this means you can use one address to connect to Astrid despite being on different networks.  On Mac and iOS, this works fine; however, on some Windows and Android devices, zeroconf is broken, and Astrid will require an IP address.

When Astrid is advertising its own Hotspot Network (typically on mobile deployments), the IP address is likely to be 10.0.0.5 as Astrid is generating that network. When connected to your home network, it will be whatever DHCP address your home network assigned.  This information is displayed on the [Astrid Mini Display](MiniDisplay.md).


## Connectivity WiFi and Hotspot

Astrid can run as it's own Access Point WiFi Hotspot or connect to a WiFi Router (e.g. a Home WiFi Network), these are called Hotspot and WiFi respectively.

When Astrid starts up, it is always in Hotspot mode and can be accessed as:

| Setting | Value |
| --------- | -------------- |
| Wi-Fi SSID | AstridHotspot |
| Wi-Fi Password | iotaiota |
| Hostname | astrid.local (or 10.0.0.5) |

In Hotspot mode, Astrid does not have access to the internet so is unable to be upgraded or download plate solve files, astronomy tables or search for astronomical objects that require online access.

This would be the typical scenario when observing in the field where internet access wasn't available.

Sometimes (near hotels, houses etc.), there can be many wifi networks and the AstridHotspot may not be listed as your WiFi network list maybe short, just enter the Hotspot name as "Other" etc.

To connect to the internet, you need to connect to a Wifi Router (for example a home router).  There are 2 ways to do this:

* [Astrid Mini Display](MiniDisplay.md) (connect over USB and press one of the 3 buttons)
* Connect your device to the Hotspot network, VNC in, and double tap/click "WiFi Connect" on the desktop. 

To manage Wi-Fi connections (network names/passwords), these can be configured via the "Wifi Setup" icon on Astrid's desktop under "Astrid Tools".

If you are ever having problems finding Astrid, then look on your list of networks to see if AstridHotspot is visible and connect to it.  Otherwise you'll find it on your WiFi Network if you switched to that.  Use the [Mini Display](MiniDisplay.md) to determine where your network is and the status it has.

Astrid can also handle multiple networks, however multiple networks at the same location should be avoided to prevent confusion as to which network you are connecting too.  But if you have 2 places (say your home and an astronomy club), then there's a case for entering multiple networks.

The ethernet port flashes alternate Green/Yellow when connected to a known WiFi Network and is solid Green/Yellow when Astrid is generating it's own Wifi Hotspot.

##### If you are hot-spotting through a phone to connect to Astrid, be aware that some cellular plans limit throughput through the phones hotspot and may result in very slow VNC response.

### Ethernet (wired connection)

***Note: Astrid over internet is not supported***

Astrid also has an ethernet port. Plug in your ethernet connection and [Mini Display](MiniDisplay.md) will indiciate the IP address and hostname to VNC too.

Now connect over VNC, run a terminal and type:

> sudo systemctl stop dnsmasq.service

To set back to the normal behaviour, shutdown Astrid (i.e. power off), remove the ethernet cable and power on Astrid.

## First Light

When Astrid is started for the first time, no Wi-Fi networks are configured and it will default to 

|           |                |
| --------- | -------------- |
| Wi-Fi SSID | AstridHotspot |
| Wi-Fi Password | iotaiota |
| Hostname | astrid.local (or 10.0.0.5) |

To connect, you will need to connect to this Wi-Fi network and you will need to use VNC, see [Connect Via VNC](#connect-via-vnc).  Once connected, you can use the "Wi-Fi Setup" icon on your desktop to add Wi-Fi networks you require.

When using Astrid for the first time, or with a new telescope / focal reducer configuration, it's important to determine the focal length and configure the [platesolver](Platesolver.md).  See [Platesolver](Platesolver.md) for more information.  Once plate solving is working, then you can Polar Align (if an equatorial mount) and then goto a bright star and focus precisely with a Bahtinov mask.


## Connect Via VNC

Connection to the Astrid app and desktop is through a VNC Client over Wi-Fi.  You can access Astrid with the following devices:

* Laptop (macOS, Windows, Linux, Raspberry Pi)
* Tablet/iPad (iOS or Android)
* Phone (iOS or Android) *small screen size = poor user experience*

For convenience in mobility and user experience, whilst moving around the telescope, we use an iPad with a larger screen size.

The VNC Client we recommend is the free [RealVNC VNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) (note you may be prompted for a free trial, but it's not necessary).  Other VNC clients may or may not work.

**IMPORTANT: There are 2 versions of RealVNC; RealVNC Viewer and RealVNC Connect. RealVNC Connect is a paid-for product, and the website and product itself are designed to pull you into purchasing the paid product by mistake. Be sure to download RealVNC Viewer using the link above.**

**After installing you'll be presented with a screen asking you to sign in and send anonymous usage data. Uncheck the send anonymous usage data checkbox, and click "Use RealVNC Viewer without signing in".  Never click the "Sign In" button.**

When setting up the client, we suggest you use "astrid.local" for the hostname instead of an IP address.  As you may access Astrid on different networks or its Access Point, using "astrid.local" instead of an IP address removes the need to have a different connection for each network. However if you have mDNS/Bonjour issues, then you may need to use the IP address.  [Astrid Mini Display](MiniDisplay.md) lists both options.

##### Please note that it may take 1-2 mins after connection for "astrid.local" to be visible on the network.
	
To add Astrid to VNC Viewer:

1. Click on the "+" button
2. Address: astrid.local  (or 10.0.0.5 on windows)
3. Name: astrid.local  (or 10.0.0.5 on windows)
4. Picture Quality: Automatic
5. Interaction: Touch Panel (Tablet) or Mouse (Computer)
6. Update desktop preview: On or Off
7. Click Done

The username / password to login to Astrid when prompted via VNC:

|           |                |
| --------- | -------------- |
| Login | pi |
| Password | iota |

### Entering Text Into Astrid

Text in VNC Viewer is entered by tapping the keyboard icon.  When entering text, be aware that you must **ALWAYS** press "Return" or "Enter (some computers)"  after the text has been entered so that the text is accepted.

### Powering Off

Quitting or closing the VNC connection, does not shut down Astrid.  
**ALWAYS REMEMBER TO SHUTDOWN ASTRID AND WAIT 15 SECONDS AFTER GREEN LIGHT STOPS FLASHING ON THE SIDE BEFORE REMOVING POWER TO AVOID SD CARD AND USB FLASH DRIVE CORRUPTION.**


	
## Internet Access

Astrid is designed for both offline and online use.  Astrid currently does not contain star catalogs, therefore to find a target that is not already saved, it uses Simbad which requires internet access.

Target objects can either be entered via Astrid for offline use (*custom Objects or Save from Simbad*) or copied onto the corresponding objects.json(*custom objects*) or occultations.json on the USB Drive.

## Upgrades

Astrid uses the Rapid Development model and should be connected to the internet and upgraded frequently.

## Focal Reducers And Length

Focal length will depend on the focal reducers used and the distance the camera sensor is from a lens or the telescope.  The typical requirement of an accurate back focus may not be necessary with ASTRID due to the smaller field of view.
 	
If using the IOTA 0.5X Focal Reducer, be aware that you may need to insert spacer rings to get the maximum focal reduction.  Most setups you 2 or 1 5mm rings.
 	
[IOTA Focal Reducer](https://occultations.org/night-eagle-2-pro-astro-edition-ordering-page/)

## Multiple Astrids

Each Astrid should have a unique hostname to avoid confusion about which one you are connecting to.

You can change the hostname as follows:

1. Make sure only 1 Astrid is on and connect to it via VNC.
2. Double click/tap the terminal icon top left (black rectangle with >\_)
3. Type:    sudo raspi-config
4. Choose: 1. System Options	(use cursor arrows, tab and enter to navigate)
5. Choose S4 Hostname
6. Enter the hostname you require (do not add .local)
7. Select OK and then Finish
8. When prompted to reboot, select Yes

Now update your VNC Address to point to the new hostname.local

## Our Setup

We use an iPad (with brightness turned down so that it lasts the night) to access Astrid.  This gives us the ability to easily move around the scope and no requirement to bring a table to place a laptop on, or bring power for it.

For Wi-Fi we have the following configured in Astrid:

* Home Network
* AC750 Tp-Link Travel Router (for Mobile deployments)

Astrid then automatically connects to our home network, or the travel router when we're mobile.  If we need a Simbad lookup, then we just enable the hotspot on the phone, and after a few seconds, the travel router connects to the hotspot automatically and Astrid has internet for object searches.

By no means is the Travel Router required, we just find it convenient for all situations (good cellular, poor cellular), as well as multiple connections and increased Wi-Fi range.  This particular travel router is low-powered and will easily run off a small 10Ah USB power pack.

For telescope/mount (focal length 732mm):

* Celestron EdgeHD 9.25"
* 0.7X Celstron Focal Reducer
* 0.5X IOTA Reducer (Ted Blank)
* ZWO AM5 Mount
	* Dakota 12V Lithium Battery (54Ah, but overkill, 10Ah-23Ah is sufficient)

We also have some Astrids configured for standalone in the field (Hotspot and no Router).

## SSH And SFTP

To ssh or sftp to Astrid:

* ssh pi@astrid.local
* sftp pi@astrid.local

The password is: iota

## Prepointing

Astrid has the ability to automatically calculate prepointing positions without needing star charts or setup at a specific time, such that once
setup, the star drifts into view and recording starts automatically.

Prepointing is useful in certain situations, for example:

* Unattended single or multiple setups
* Setups with no Goto / Tracking (i.e. statically pointed)
* Rough polar alignment

For the best success with prepointing:

* Short focal lengths ( <500mm )
* Short occultations

To prepoint, click the Prepoint button when Occultations is selected in Object.  The process is iterative, so click Photo, Solve, Sync and then adjust the mount and repeat until the error is minimal, the following metrics reported are useful:

Pos Error(%FOV) = The positional error in percentage of the height of the FOV for the sensor.  This is another way of quantifying the position error displayed in the arrows.  I.E. I have this much error, am I close enough to the center?  It's suggested to adjust the mount until 10% or better is reached.  At 50%, it is half the field of view, and that will mean that the star is at the edge of the frame.

FOV Size = Size of the Field of View

Drift Time 75% FOV: This is the number of minutes it takes to drift across 75% of the FOV Height.  The occultation event should fit within this time.

When prepointing is adjusted, then the Auto Record button can be pushed to auto record when the event begins.

## Auto Record and OWCloud

Enter your events into OWCloud, sync to Astrid and use Auto Record.  If you do this, it removes the chances for error and will setup the ideal recording time for binary asteroid and binary star discovery without wasting space on your USB drive.


## Player

Astrid Player (available on the desktop) can be used to load an Astrid Recording, view the occultation, and also Plate Solve and mark the target.  The plate solved image can then be saved as a Fits Finder and loaded into PyOTE to assist with locating the target in PyOTE.

## Light Curve Analysis

The recommended tool for analyzing light curves from Astrid is Bob Andersons awesome [PyMovie](https://pypi.org/project/pymovie/) and [PyOTE](https://pypi.org/project/pyote/)

Starting from version 3.9.4 of PyMovie, the RAVF Video format used by Astrid is natively supported.

Other light curve analyzers currently do not support the RAVF video format.  Astrid Player can be used to convert to fits format for other analyzers.

## Occult4 Searches

Astrid supports the ability to fast search through Occult Element files generated by Occult4.  These files are .xml files in the following format:


	<Occultations>
  		<Event>
    		<Elements>JPL#47+INTG:2023-Dec-05,0.26,2024,1,4,22.964245,0.079998,0.530961,-6.425429,0.968085,-0.000416,-0.000204,0.000001,0.000000</Elements>
   			<Earth>20.9283,24.8261,-163.23,-22.69,False</Earth>
    		<Star>UCAC4 575-037911,7.27148376,24.8686687,13.38,13.14,12.75,0.0,0,,7.29621845,24.8261384,4.55,4.48,0,0,0</Star>
    		<Object>22268,1981 EJ26,17.67,3.010,1.3150,0,0,-3.156,6.47,,0.2,0</Object>
			<Orbit>0,120.9367,2024,1,5,298.2050,35.0191,1.5547,0.12887,2.13202,1.85727,15.04,5.0,0.15</Orbit>
    		<Errors>1.215,0.0190,0.0005,97,0.0190,Known errors,1.05,0,0,0</Errors>
    		<ID>20240104_037911,60308.83</ID>
  		</Event>
  		<Event>
    		<Elements>JPL#51+INTG:2023-Dec-05,0.36,2024,1,4,22.984674,0.049755,0.572965,-6.623967,0.575224,-0.000015,0.000333,0.000001,0.000000</Elements>
    		<Earth>16.2929,19.4626,-163.54,-22.69,False</Earth>
    		<Star>UCAC4 548-036348,6.98381004,19.4952800,15.09,14.74,14.24,0.0,0,,7.00767580,19.4625705,2.64,2.69,0,0,0</Star>
    		<Object>10456,Anechka,17.29,4.207,1.4969,0,0,-2.751,3.38,,0.4,0</Object>
    		<Orbit>0,165.6603,2024,1,5,85.3013,211.7375,2.0516,0.04348,2.37880,2.27538,14.26,5.0,0.15</Orbit>
    		<Errors>1.253,0.0123,0.0009,96,0.0123,Known errors,1.00,0,0,0</Errors>
    		<ID>20240104_036348,60308.83</ID>
  		</Event>
  		...
	</Occultations>

To integrate one of these files into Astrid, please do the following:

1. Rename it to something like MyName\_2024\_Asteroids\_Jan.xml or MyName\_2024\_Asteroids.xml
2. If there are a significant number of events (e.g. more than 20,000 - 40,000), it might be advisable to split the events into months.  Although Astrid will handle many more events than this, your search time will be faster
3. With internet connected, under Object, click Add and "Search Occelmnt XML Lists" and follow the prompts.  This will download and install Steve Prestons occultation predictions and create the folder required for the this feature
4. On a desktop computer, copy your xml file of events into the predictions folder on the Astrid USB Drive
5. Place USB Drive back in Astrid, and under "Object", click "Add" and "Search Occelment XML Lists" and choose your xml list which should be visible now.

The predictions folder and/or your xml file can be copied between USB Drives or to the USB Drive if you are updating.

Please note that clicking on the event to link to OWCloud will only work with IOTA-tagged events.  This is a limitation of OWCloud, and there are no plans for OWCloud to implement linking of non-IOTA tagged events at this time.

Once an event is identified, hit the "+" to add the event to Astrid.
The Occult Element format does not provide an error time in it's specification, so Astrid defaults the error to 0.001s, please determine the error via other means and update so the start/end times are calculated correctly automatically for the event.
