#!/bin/sh


# Switch Chromium Hardware Acceleration Off

chromeHardwareAccelerationOff()
{
	CONFIG_FILE="/home/pi/.config/chromium/Local State"

	TMP=`/usr/bin/grep '"hardware_acceleration_mode":{"enabled":true}' "$CONFIG_FILE"`
	if [ ! -z "$TMP" ];then
		echo "Switching Hardware Acceleration OFF for Chromium"
		/usr/bin/sed 's/\"hardware_acceleration_mode\"\:{\"enabled\"\:true}/\"hardware_acceleration_mode\"\:{\"enabled\"\:false}/' "$CONFIG_FILE" > "$CONFIG_FILE".tmp
		/usr/bin/cat "$CONFIG_FILE".tmp > "$CONFIG_FILE"
		/usr/bin/rm -f "$CONFIG_FILE".tmp
	fi
}



echo "*************************************************************"
echo "*                      Upgrading ASTRID                     *"
echo "* ASTRID MUST BE ABLE TO CONNECT TO THE INTERNET TO UPGRADE *"
echo "*************************************************************"
echo
echo "Proceed? (y/n)"
read line
if [ "$line" != "y" ];then
	echo "Upgrade aborted..."
	echo "Press <RETURN> to continue"
	read line
	exit 1
fi


echo "Downloading upgrade files..."
cd /home/pi
git clone https://github.com/ChasinSpin/astrid.git -- /home/pi/astridUpgrade
if [ $? != 0 ];then
	echo "Error: Git transfer failed. Internet Connection?"
	echo "Press <RETURN> to continue"
	read line
	exit 1
fi

# Do any upgrade specific stuff here
echo "Upgrading..."

# Install
echo "Installing..."
cd /home/pi
/usr/bin/mv astrid astridOld
/usr/bin/mv astridUpgrade astrid
cd /home/pi/astrid
./install.sh

chromeHardwareAccelerationOff

/usr/bin/rm -rf /home/pi/astridOld
echo "**** Upgrade complete ****"
echo "Press <RETURN> to REBOOT"
read line
/usr/bin/sudo reboot

exit 0
