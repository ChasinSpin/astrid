# Raspberry Pi Complete Installation Instructions
	
Important, we use Bullseye here due to the PiCamera2 Library requirement.

## Install Raspberry Pi Image
	Install 2023-05-03-raspios-bullseye-armhf.img.xz: Raspberry Pi OS with desktop 
	(32bit Bullseye image) using  Raspberry Pi Imager with the following settings:
	
		Hostname: astrid.local
		Enable SSH: Use password authentication
		Set username and password:
			Username: pi
			Password: iota
		Configure wireless LAN:
			SSID: 
			Password:
			Wireless LAN country: US
		Set local settings:
			Time zone: America/Edmonton
			Keyboard layout: us
				
	Boot SD Card in Raspberry Pi, when booted:
		ssh pi@astrid.local
		
## Update image (DO NOT USE, for future reference)
		
		# DISABLED ON 2023-05-03 Bullseye Release DO NOT USE
		# sudo apt update			# If this gives a message about E: Release file...., re-run it
		# sudo apt -y full-upgrade 	# Note: we want to do this for all the camera changes
		# sudo apt install -y python3-picamera2
			
## Setup SPI & Localization
		
		sudo raspi-config
			Interface Options
				SPI: Enable
			Localization Options
				Timezone: None of the Above: UTC
			Update      (This updates raspi-config only)
			Finish
		sudo reboot
		
		ssh pi@astrid.local
		
## Setup ATmega328pb programming environment
		# Install environment to program ATmega328pb
		sudo apt-get -y install automake bison flex gcc-avr binutils-avr avr-libc # (maybe avr-lib instead of avr-libc)
		
		# Add ATmega328PB to avr-gcc
		# Reference: https://blog.koipond.org.uk/archives/105
		# Reference: https://stuvel.eu/post/2021-04-27-atmega328pb-on-gcc/
		# Reference: https://wellys.com/posts/avr_c_328pb/
		cd
		wget http://packs.download.atmel.com/Atmel.ATmega_DFP.2.0.401.atpack
		unzip -d microchip-avr-dfp Atmel.ATmega_DFP.2.0.401.atpack
		sudo cp microchip-avr-dfp/gcc/dev/atmega328pb/avr5/crtatmega328pb.o microchip-avr-dfp/gcc/dev/atmega328pb/avr5/libatmega328pb.a /usr/lib/avr/lib/avr5
		sudo cp  microchip-avr-dfp/include/avr/iom328pb.h /usr/lib/avr/include/avr
		sudo cp /usr/lib/avr/include/avr/io.h /usr/lib/avr/include/avr/io.h~
		sudo vi /usr/lib/avr/include/avr/io.h
			# Search 328P and add after:
				#elif defined (__AVR_ATmega328PB__)
				#  include <avr/iom328pb.h>
		rm -rf microchip-avr-dfp
		rm Atmel.ATmega_DFP.2.0.401.atpack
				
		git clone https://github.com/kcuzner/avrdude 
		cd avrdude/avrdude
		./bootstrap && ./configure && sudo make install
		cd
		sudo vi /usr/local/etc/avrdude.conf
			# Search m328p and add after:
			part parent "m328"
 			   id                  = "m328pb";
    			desc                = "ATmega328PB";
    			signature           = 0x1e 0x95 0x16;

    			ocdrev              = 1;
			;
	
## Install QT, AstroPy, Astrometry, xmltodict and photutils
		# Install QT Designer and OpenCv
		sudo apt -y install qtcreator
		sudo apt -y install python3-opencv
				
		# Install AstroPy
		pip3 install astropy
	
		# Install Astrometry.net
		# Reference: https://g5555.neocities.org/astrometry
		sudo apt-get -y install astrometry.net
		#sudo apt-get -y install astrometry-data-tycho2
		sudo vi /usr/lib/python3/dist-packages/astrometry/util/fits.py
			# Change all np.bool to np.bool_
			
		# Install xmltodict
		pip3 install xmltodict
		
		pip3 install photutils
				    		
## Install Indilib
    	# Install INDI from source:
    	# https://github.com/indilib/indi
    		# Pre-requisites
    		sudo apt-get install -y \
			  git \
			  cdbs \
			  dkms \
			  cmake \
			  fxload \
			  libev-dev \
			  libgps-dev \
			  libgsl-dev \
			  libraw-dev \
			  libusb-dev \
			  zlib1g-dev \
			  libftdi-dev \
			  libgsl0-dev \
			  libjpeg-dev \
			  libkrb5-dev \
			  libnova-dev \
			  libtiff-dev \
			  libfftw3-dev \
			  librtlsdr-dev \
			  libcfitsio-dev \
			  libgphoto2-dev \
			  build-essential \
			  libusb-1.0-0-dev \
			  libdc1394-dev \
			  libboost-regex-dev \
			  libcurl4-gnutls-dev \
			  libtheora-dev
			
			# Get the code
			cd
			mkdir -p ~/Projects
			cd ~/Projects
			git clone --depth 1 https://github.com/indilib/indi.git
			
			# Build indi-core (cmake)
			mkdir -p ~/Projects/build/indi-core
			cd ~/Projects/build/indi-core
			cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Debug ~/Projects/indi
			make -j4
			sudo make install
			make clean
			
		# Install pyindi-client
		# Dependancies
		sudo apt-get -y install python-setuptools python-dev swig libcfitsio-dev libnova-dev
		
		#DO NOT INSTALL THIS AS WE'RE COMPILING INDI FROM SOURCE AND THEN pyindi-client won't install
			# sudo apt-get -y libindi-dev 
			
		# Install from source
		cd
		wget https://github.com/indilib/pyindi-client/archive/refs/heads/master.zip
		unzip master.zip
		rm master.zip
		cd pyindi-client-master
		sudo python3 setup.py install
		
## Enable serial debug for OTEStamper
		# Enabling debugging serial print's from the ATmega328p firmware and 
		# enabling Turbo mode so Pi doesn't go into energy saving mode and slow down SPI
		sudo vi /boot/config.txt		# Add at the end
			#dtoverlay=uart5	# We use this for an interrupt now!
			force_turbo=1	

## Configuring GPS & PPS on Raspberry Pi for system time
[Reference](https://austinsnerdythings.com/2021/04/19/microsecond-accurate-ntp-with-a-raspberry-pi-and-pps-gps/)

Statum 1 Time

	sudo apt install pps-tools gpsd gpsd-clients chrony
	sudo vi /boot/config.txt
		Add:
			dtoverlay=pps-gpio,gpiopin=4
			enable_uart=1
			init_uart_baud=9600	
			
	sudo vi /etc/modules
		Add:
			pps-gpio
			
	sudo vi /etc/default/gpsd
		Change:
			USBAUTO="true"
		To:
			USBAUTO="false"
		(This prevents indilib mounts being stolen by the GPS, e.g. SkyWatcher)
			
	sudo raspi-config
		Interface Options/Serial Port:
			Would you like a login shell to be accessible over serial?:  No
			Would you like the serial port hardware to be enabled?: Yes
			Finish / Reboot now: No
	sudo systemctl disable serial-getty@ttyS0.service
	sudo systemctl stop serial-getty@ttyS0.service
	sudo systemctl disable serial-getty@ttyAMA0.service
	sudo systemctl stop serial-getty@ttyAMA0.service
	sudo systemctl disable hciuart
	sudo systemctl stop hciuart
	sudo reboot
	
	ssh pi@astrid.local
	
	cat /dev/ttyS0
	Check GPS messages are coming in.  Note "unknown msg" is due to
	the tty echoing every command back to the GPS, to fix:
	
	sudo vi /etc/systemd/system/no-serial-echo.service

		[Unit]
		Description=Disable serial echo
		DefaultDependencies=no
		Before=basic.target
		After=sysinit.target
		
		[Service]
		Type=oneshot
		ExecStart=/bin/stty -F /dev/ttyS0 -echo
		
		[Install]
		WantedBy=basic.target
	
	sudo systemctl enable no-serial-echo
	sudo reboot

	ssh pi@astrid.local
	cat /dev/ttyS0    (and check the GPS messages are now clean with no unknowns)
	sudo vi /etc/default/gpsd
	
		Change to:
			DEVICES="/dev/ttyS0 /dev/pps0"
			GPSD_OPTIONS="-n"
			
	sudo cp /lib/systemd/system/gpsd.service /etc/systemd/system/gpsd.service
	sudo systemctl unmask gpsd
	sudo systemctl daemon-reload
	sudo systemctl enable gpsd
	sudo systemctl start gpsd
	
	sudo vi /boot/config.txt
		# This fixes a bug causing the pps_gpio driver to timeout
		# Reference: https://github.com/raspberrypi/linux/issues/5430
		Add: 
			arm_64bit=0
	sudo reboot
	
	ssh pi@astrid.local
	ps -ef | grep gpsd  # Check gpsd process exists
	Use gpsmon to confirm data is being used, and fix is obtained and PPS is working etc.
	lsmod | grep pps
		Results: pps_gpio               16384  3
	sudo ppstest /dev/pps0 
		(this should spit out a PPS signal every second provided arm_64bit=0, otherwise there will be a timeout after the first pulse)
	sudo vi /etc/chrony/chrony.conf
		Add:
			refclock SHM 0 refid NMEA precision 1e-1 offset 0.13115 noselect
			refclock PPS /dev/pps0 refid PPS lock NMEA precision 1e-9 offset 0.0 prefer
			
		Change to:
			makestep 1 -1
	sudo reboot
	
## Check GPS & PPS are working
	ssh pi@astrid.local
		chronyc sources -v
		
		After a while, PPS should have * by it confirming its the source being used.
		* = active source
		+ = good source and will be used if active source not available
		x = false ticker, which means source isn't being used, NMEA will always be this as we used PPS
		# = Locally connected source
		? = Haven't determined the status of the source yet
		
		[] = how far chrony is from the source
		Last column (after +/- includes latency to the NTP source as well as how far out of sync chrony thinks it is)
		chronyc sourcestats
		
		To sync the system time immediately to the chronyc:
			chronyc makestep
		
		References:
		https://jfearn.fedorapeople.org/fdocs/en-US/Fedora_Draft_Documentation/0.1/html/System_Administrators_Guide/sect-Checking_if_chrony_is_synchronized.html
		https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/ch-configuring_ntp_using_the_chrony_suite
		https://robrobinette.com/pi_GPS_PPS_Time_Server.htm#GPS_With_PPS_Testing_&_Troubleshooting
		https://chrony-project.org/doc/3.4/chrony.conf.html
		
		
## Install VNC
		# Install Regular VNC		
 		sudo raspi-config
			Display Options/VNC Resolution/1280x1024
			Interface Options/VNC/Yes/OK
			Finish/Reboot Now
		Login to the desktop via RealVNC on the mac: astrid.local
		
		# Test connection to VNC
		Use RealVNC's VNC Viewer
	
		# May need this, but disabled for now
		# Click VNC icon at the top of the desktop, click the pull down menu (top right)
		# Choose Options/Troubshooting and check "Enable direct capture mode", click OK
		# VNC will hang	
		
## Setup Camera Sensor

	sudo vi /boot/cmdline.txt
	Add:
			cma=128M

## IMX296 Global Shutter Mono/Color
	 	sudo vi /boot/config.txt
		Add:
			dtoverlay=imx296
		sudo reboot

## IMX477 Raspberry Pi HQ (DO NOT USE)
    	# Enable IMX477 Sensor XVS Trigger output
    	sudo vi /boot/cmdline.txt
    		imx477.trigger_mode=1  	# Add this
	 
	 	# Disable Star Eater for IMX477 Sensor
	 	sudo vi /boot/cmdline.txt:
			imx477.dpc_enable=0		# Add this
		sudo reboot
			
## OV9281 (DO NOT USE)
	 	sudo vi /boot/config.txt
		Add:
			dtoverlay=ov9281
		sudo reboot
			
## Test Camera		
			
		# Test camera
		Launch Astrid, check can see camera over VNC
		sudo poweroff


## Change Desktop Background
		# Change background
		Raspberry Pi Icon / Preferences / Appearance Settings / Change Picture to aurora.jpg 
		
## Prevent Desktop from Prompting To Execute
			
		# To prevent it asking to execute in terminal
		Open up the file manager (double yellow folders)
		Edit/Preferences/General
		Check "Don't ask options on launch executable file"
		Click Close

## Install AutoHotspot
		
	Reference: https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/183-raspberry-pi-automatic-hotspot-and-static-hotspot-installer

	curl "https://www.raspberryconnect.com/images/hsinstaller/Autohotspot-Setup.tar.xz" -o AutoHotspot-Setup.tar.xz
	tar -xvJf AutoHotspot-Setup.tar.xz
	sudo raspi-config
		Localization / Set WLAN Country to US
	cd Autohotspot
	sudo ./autohotspot-setup.sh
	Option 2
		
	Wifi hotspot: RpiHotspot
	Wifi password is 1234567890
	IP: 10.0.0.5
		
	Option 7. Change to:
		Access Point SSID: AstridHotspot
		Password: iotaiota
			
	crontab -e 
	Add:
		* * * * * sudo /usr/bin/autohotspot >/dev/null 2>&1

## Install Astrid			
			
		# Install the astrid software
		cd
		See 1Password for configuring git account
		#git config --global user.name "XXXXXXXXX"
		#git config --global user.email "XXXXX@XXXXXXX"
		#git config --global credential.helper 'cache --timeout=10000000'
		git clone https://github.com/ChasinSpin/astrid.git
		cd astrid
		./install.sh
			
## Install Indi 3rd Party Focusers and Mounts
		cd ~/astrid/scripts
		./install_indi_3rdparty.sh
		
## Run Astrid and download astropy needed downloads for offline use

With simulator mount:

	* Do a custom search for vega, then a goto
		which downloads:
			* https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat
			* https://datacenter.iers.org/data/9/finals2000A.all
	* Do a prepoint to force AltAz conversion (this forces a download)

## Run Chromium once

Start and exit chromium (so we can change settings in the upgrade later)

## Run Astrid Upgrade

Run Astrid Upgrade

## Remove networks and history

		cd
		rm .bash_history
		
		Remove any networks used during this build:
		sudo vi /etc/wpa_supplicant/wpa_supplicant.conf;sync;sync;sync;sudo poweroff
		
## Create Image
	# Create image on Mac using PiLess https://github.com/ChasinSpin/PiLess 
	sudo ./PiLess.sh imagename	
	e.g. sudo ./PiLess.sh ../2023-08-02-astrid