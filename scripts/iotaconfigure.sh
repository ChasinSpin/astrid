#!/bin/sh
TMP_FILE="/tmp/iotaconfigure.$$"


sudocmd()
{
	sudo sh -c "$1" 2>&1 | /usr/bin/grep -v "Name or service not known"
}

echo "This tool configures Astrid and is intended for use by IOTA to"
echo "speed up building units for the store..."
echo
echo "Input the hostname desired (do not include .local),"
echo "for example: astrid-0106   and press <RETURN>"
echo "This will configure the Hostname for the device and the Wifi Hotspot"

echo -n "Enter hostname> "
read HOSTNAME

# Conifgure hosts
sudocmd "/usr/bin/cat /etc/hosts | /usr/bin/grep -v '127.0.1.1' > $TMP_FILE"
echo -n "Changing hostname and astrid hotspot..."
sudocmd "echo '127.0.1.1	$HOSTNAME' >> $TMP_FILE"
sudocmd "/usr/bin/cat $TMP_FILE > /etc/hosts"
sudocmd "/usr/bin/rm $TMP_FILE"

# Configure hostname
sudocmd "echo '$HOSTNAME' > /etc/hostname"

# Configure Astrid Hotspot Name
sudocmd "/usr/bin/sed 's/ssid=.*/ssid=$HOSTNAME/' /etc/hostapd/hostapd.conf > $TMP_FILE"
sudocmd "/usr/bin/cat $TMP_FILE > /etc/hostapd/hostapd.conf"
sudocmd "/usr/bin/rm $TMP_FILE"
echo done

echo
echo "** Astrid formatted USB Drive must be inserted at this stage **"
echo -n "Qualify Drive? (y/n) > "
read line
if [ "$line" = "y" -o "$line" = "Y" ]; then
	/home/pi/astrid/scripts/qualify_drive.py
fi

echo
echo "** ENSURE YOU ARE ON YOUR HOME WIFI NETWORK BEFORE UPGRADING **"
echo "** NOTE: If you're on Hotspot and are just switching now, you will **"
echo "** need to change your machine network connection and reconnect **"
echo "** with VNC to continue **"
echo -n "Upgrade Now? (y/n) > "
read line
if [ "$line" = "y" -o "$line" = "Y" ]; then
	/home/pi/astrid/upgrade.sh noreboot
fi

echo 
echo "After reboot, please test and then run:  ~/astrid/scripts/cleanship.sh"

echo "Press <RETURN> to REBOOT"
read line
/usr/bin/sudo reboot

exit 0
