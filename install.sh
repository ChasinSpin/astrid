#!/bin/sh



# Switch Chromium Hardware Acceleration Off

chromeHardwareAccelerationOff()
{
        CONFIG_FILE="/home/pi/.config/chromium/Local State"

        TMP=`/usr/bin/grep '"hardware_acceleration_mode":{"enabled":true}' "$CONFIG_FILE"`
        if [ ! -z "$TMP" ]; then
                echo "Switching Hardware Acceleration OFF for Chromium"
                /usr/bin/sed 's/\"hardware_acceleration_mode\"\:{\"enabled\"\:true}/\"hardware_acceleration_mode\"\:{\"enabled\"\:false}/' "$CONFIG_FILE" > "$CONFIG_FILE".tmp
                /usr/bin/cat "$CONFIG_FILE".tmp > "$CONFIG_FILE"
                /usr/bin/rm -f "$CONFIG_FILE".tmp
        fi
}



# Switch OS Upgrade Notifications Off

osUpgradeNotificationsOff()
{
	LXDE_PANEL_OLD="/etc/xdg/lxpanel/LXDE-pi/panels/panel"
	LXDE_PANEL_NEW="/home/pi/astrid/install/lxde-panel"

	TMP=`/usr/bin/grep "type=updater" "$LXDE_PANEL_OLD"`
	if [ ! -z "$TMP" ]; then
		echo "Switching OS Upgrade Notifications OFF"
		sudo sh -c "/usr/bin/cat \"$LXDE_PANEL_NEW\" > \"$LXDE_PANEL_OLD\""
	fi
}



# Switch Auto Launch File Manager when USB Flash Drive Inserted Off

fileManagerAutoLaunchOff()
{
	LXDE_PCMANFM_BKP="/home/pi/.config/pcmanfm/LXDE-pi/pcmanfm.conf~"
	LXDE_PCMANFM_NEW="/home/pi/.config/pcmanfm/LXDE-pi/pcmanfm.conf"

	TMP=`/usr/bin/grep "autorun=1" "$LXDE_PCMANFM_NEW"`
	if [ ! -z "$TMP" ]; then
		echo "Switching File Manager USB Drive Auto Launch OFF"
		/usr/bin/sed 's/autorun=1/autorun=0/' "$LXDE_PCMANFM_NEW" > "$LXDE_PCMANFM_BKP"
		/usr/bin/mv "$LXDE_PCMANFM_BKP" "$LXDE_PCMANFM_NEW"
	fi
}


# Install healpix

installHealpix()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep cdshealpix`
	if [ -z "$TMP" ];then
		echo "Installing cdshealpix"
		/usr/bin/pip3 install cdshealpix==0.6.4
	fi
}



# Install pyqtree

installPyqtree()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep Pyqtree`
	if [ -z "$TMP" ];then
		echo "Installing pyqtree"
		/usr/bin/pip3 install pyqtree==1.0.0
	fi
}



# Install openpyxl

installOpenpyxl()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep openpyxl`
	if [ -z "$TMP" ];then
		echo "Installing openpyxl"
		/usr/bin/pip3 install openpyxl==3.1.2
	fi
}



# Install kmeans1d

installKmeans1d()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep kmeans1d`
	if [ -z "$TMP" ];then
		echo "Installing kmeans1d"
		/usr/bin/pip3 install kmeans1d==0.3.1
	fi
}



# Install sgp4

installSgp4()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep sgp4`
	if [ -z "$TMP" ];then
		echo "Installing sgp4"
		/usr/bin/pip3 install sgp4==2.24
	fi
}



# Install spacetrack

installSpacetrack()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep spacetrack`
	if [ -z "$TMP" ];then
		echo "Installing spacetrack"
		/usr/bin/pip3 install spacetrack==1.4.0
	fi
}



# Install adafruit-board-toolkit

installAdafruitBoardToolkit()
{
	TMP=`/usr/bin/pip3 list | /usr/bin/grep adafruit-board-toolkit`
	if [ -z "$TMP" ];then
		echo "Installing adafruit-board-toolkit"
		/usr/bin/pip3 install adafruit-board-toolkit==1.1.1
	fi
}



# Install QCharts

installQCharts()
{
	TMP=`/usr/bin/apt list --installed | /usr/bin/grep python3-pyqt5.qtchart`
	if [ -z "$TMP" ];then
		echo "Installing QCharts"
		/usr/bin/sudo /usr/bin/apt-get install -y python3-pyqt5.qtchart
	fi
}



# Install lsscsi

installLsScsi()
{
	TMP=`/usr/bin/apt list --installed | /usr/bin/grep lsscsi`
	if [ -z "$TMP" ];then
		echo "Installing lsscsi"
		/usr/bin/sudo /usr/bin/apt-get install -y lsscsi
	fi
}



# Install mdio-tool

installMdioTool()
{
	if [ ! -f /usr/local/bin/mdio-tool ];then
		echo "Installing mdio-tool"
		cd /home/pi
		/usr/bin/git clone https://www.github.com/ChasinSpin/mdio-tool
		cd mdio-tool
		/usr/bin/mkdir build-dir
		cd build-dir
		/usr/bin/cmake ..
		/usr/bin/make
		/usr/bin/sudo /usr/bin/make install
		/usr/bin/make clean
		cd ..
		/usr/bin/rm -rf build-dir
	fi
}



# Install Autohotspot Setup

installAutoHotspot()
{
	echo "Installing autohotspot changes"
	/usr/bin/cp /home/pi/astrid/scripts/autohotspot-setup.sh /home/pi/Autohotspot/autohotspot-setup.sh
	/usr/bin/cp /home/pi/astrid/scripts/autohotspot-direct.service /home/pi/Autohotspot/config/autohotspot-direct.service
	/usr/bin/cp /home/pi/astrid/scripts/Checklist.md5 /home/pi/Autohotspot/config/Checklist.md5
	sudo /usr/bin/cp /home/pi/astrid/scripts/autohotspot /usr/bin/autohotspot
	sudo /usr/bin/cp /home/pi/Autohotspot/config/autohotspot-direct.service /etc/systemd/system/autohotspot.service
	sudo systemctl daemon-reload
}



# Install a service, arguments = serviceFile    serviceName

installService()
{
	sudo /usr/bin/cp $1 /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable $2
	sudo systemctl start $2
	# sudo systemctl status $2	# This launches journal which uses standard input and works like "more" requiring keyboard entry... Don't use
}



# Remove AutoHotspot Crontab

autoHotspotCrontabRemove()
{
	/usr/bin/crontab -l | /usr/bin/sed '/autohotspot/d' | /usr/bin/crontab -
}


ASTRID_FOLDER="/home/pi/astrid"
APP_FOLDER="$ASTRID_FOLDER/app"
OTESTAMPER_FOLDER="$ASTRID_FOLDER/OTEStamper"


echo "Updating desktop icons..."
/usr/bin/rm -rf /home/pi/Desktop/*
/usr/bin/mkdir "/home/pi/Desktop/Astrid Tools"

/usr/bin/ln -s /home/pi/astrid/desktop/AstridApp.desktop		 /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/Player.desktop			 /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/WifiConnect.desktop		 /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/Shutdown.desktop			 /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/WifiSetup.desktop		"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/AstridUpgrade.desktop		"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/TerminateAstridThreads.desktop	"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/FormatUSBFlashDrive.desktop	"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/Diagnostics.desktop		"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/InstallMiniDisplay.desktop	"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/QualifyDrive.desktop		"/home/pi/Desktop/Astrid Tools"
/usr/bin/ln -s /home/pi/astrid/desktop/LightsOut.desktop		"/home/pi/Desktop/Astrid Tools"

echo "Installing ravf..."
pip install --no-deps ravf --upgrade

echo "Making ospi..."
cd $APP_FOLDER
./make-ospi.sh

echo "Making oteutils..."
cd "$APP_FOLDER"
./make_oteutils.sh

chromeHardwareAccelerationOff
osUpgradeNotificationsOff
fileManagerAutoLaunchOff
installHealpix
installPyqtree
installQCharts
installOpenpyxl
installKmeans1d
installSgp4
installSpacetrack
installAdafruitBoardToolkit
installMdioTool
installAutoHotspot
installLsScsi

echo "Installing firmware..."
cd "$OTESTAMPER_FOLDER/firmware"
/usr/bin/make clean
/usr/bin/make writefuses
/usr/bin/make install
/usr/bin/make clean

echo "Installing services..."
installService /home/pi/astrid/services/astrid-monitor.service astrid-monitor
installService /home/pi/astrid/services/wlan0-powermgmt-off.service wlan0-powermgmt-off

autoHotspotCrontabRemove

echo
echo "** Updated Astrid to version: "`/usr/bin/cat ~/astrid/version.txt`" **"
echo

exit 0
