#!/bin/sh

if [ $# -eq 1 -a "$1" = "noreboot" ]; then
	REBOOT=
else
	REBOOT=y
fi

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

/usr/bin/rm -rf /home/pi/astridOld
echo "**** Upgrade complete ****"

if [ ! -z "$REBOOT" -a "$REBOOT" = "y" ];then
	echo "Press <RETURN> to REBOOT"
	read line
	/usr/bin/sudo reboot
fi

exit 0
