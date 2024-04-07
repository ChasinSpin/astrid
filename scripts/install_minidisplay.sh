#!/bin/sh


DELAY_CIRCUITPY_INSTALL=20


slowExit()
{
	echo "Aborting..."
	if [ $AUTO -eq 0 ];then
		echo "Press <Return> To Exit"
		read line
	fi
	exit 2
}



usage()
{
	echo "Usage: $0 [--auto | --factory]"
	exit 1
}


getDrive()
{
	DRIVE=`/usr/bin/mount | /usr/bin/egrep "${FTDRIVE}|CIRCUITPY" | /usr/bin/cut -f3 -d" " | /usr/bin/cut -f4 -d"/"`
}



setImagesForModel()
{
	CIRCUIT_PYTHON_UF2=""
	FACTORY_RESET_UF2=""
	FTDRIVE=""

	echo
	TMP=`/usr/bin/lsusb | /usr/bin/grep "Adafruit Feather ESP32-S2 Reverse TFT"`
	if [ ! -z "$TMP" ];then
		CIRCUIT_PYTHON_UF2="adafruit-circuitpython-adafruit_feather_esp32s2_reverse_tft-en_US-8.2.9.uf2"
		FACTORY_RESET_UF2="adafruit_feather_esp32s2_reversetft_factory_reset.uf2"
		FTDRIVE="FTHRS2BOOT"
		echo "Adafruit ESP32-S2 Reverse TFT Feather Detected"
	fi

	TMP=`/usr/bin/lsusb | /usr/bin/grep "Adafruit Feather ESP32-S3 Reverse TFT"`
	if [ ! -z "$TMP" ];then
		CIRCUIT_PYTHON_UF2="adafruit-circuitpython-adafruit_feather_esp32s3_reverse_tft-en_US-8.2.9.uf2"
		FACTORY_RESET_UF2="adafruit_feather_esp32s3_reversetft_factory_reset.uf2"
		FTDRIVE="FTHRS3BOOT"
		echo "Adafruit ESP32-S3 Reverse TFT Feather Detected"
	fi

	if [ -z "$FTDRIVE" ];then
		echo "ERROR: Recognized Adafruit Device Not Found"
		slowExit
	fi
}


enterBootloader()
{
	echo
	echo "Please enter bootloader mode on Mini Display..."
	echo "Reset button is the single button on the right."
	echo "The following reset sequence needs to be executed fast, if you fail just try again..."
	echo "When successful, screen will display Green/Blue/Orange colors with 'Feather TFT' in the green part."
	echo "Timing of the Reset presses is approximately Reset<0.25s>Reset<0.5s>Reset"
	echo
	echo
	echo "** Press the reset button twice in quick succession followed by a very slight pause, and press reset once more. **"
	echo
	echo "Waiting for bootloader mode to be entered..."

	while true
	do
		getDrive
		if [ ! -z "$DRIVE" -a "$DRIVE" = "$FTDRIVE" ];then
			echo
			echo "Bootloader mode detected..."
			break
		fi
		sleep 1
	done
}



factoryDefault()
{
	getDrive

	if [ "$DRIVE" = "CIRCUITPY" ];then
		echo
		echo "Deleting files in CIRCUITPY..."
		/usr/bin/rm -rf /media/pi/CIRCUITPY/*
	fi

	sleep 1
	getDrive

	if [ -z "$DRIVE" -o "$DRIVE" = "CIRCUITPY" ];then
		enterBootloader
		echo
		echo "Copying factory reset image to drive..."
		/usr/bin/cp /home/pi/astrid/miniDisplay/uf2/$FACTORY_RESET_UF2 /media/pi/$FTDRIVE
		echo "Factory Reset Complete !"
	fi
}



installUpgrade()
{
	getDrive

	if [ -z "$DRIVE" ];then
		enterBootloader
		sleep 1
		getDrive
	fi

 	if [ "$DRIVE" = "$FTDRIVE" ];then
		echo
		echo "Copying Circuit Python image to drive..."
		/usr/bin/cp /home/pi/astrid/miniDisplay/uf2/$CIRCUIT_PYTHON_UF2 /media/pi/$FTDRIVE
		echo "Circuit python installed..."
		echo "Waiting $DELAY_CIRCUITPY_INSTALL seconds for CIRCUITPY drive to appear..."
		sleep $DELAY_CIRCUITPY_INSTALL 
	fi

	getDrive

 	if [ "$DRIVE" = "CIRCUITPY" ];then
		echo
		echo "Copying Mini Display python files to drive..."
		/usr/bin/cp -r /home/pi/astrid/miniDisplay/circuitpy/* /media/pi/CIRCUITPY
		echo "Mini Display Installation/Upgrade Completed !"
		echo
		echo "** Now press the reset button to start the Mini Display if it's not already running **"
	else
		echo "ERROR: CIRCUITPY drive not found"
		slowExit
	fi
}



#
# MAIN
#

AUTO=0
FACTORY=0

if [ $# -gt 1 ];then
	usage $0
fi

if [ $# -eq 1 ];then
	if [ "$1" = "--auto" ];then
		AUTO=1
	elif [ "$1" = "--factory" ];then
		FACTORY=1
	else
		usage $0
	fi
fi

echo "Updating Astrid Mini Display..."
echo

if [ $AUTO -eq 0 ];then
	echo "** ENSURE MINI DISPLAY IS PLUGGED INTO USB SOCKET (ANY) ON ASTRID BEFORE PROCEEDING **"
	echo "A USB cable that can provide both power AND DATA is required"
	echo
	echo "Type GO<Return> to update"
	read line
	if [ "$line" != "GO" ];then
		slowExit
	fi
else
	echo "Updating Astrid Mini Display..."
fi

setImagesForModel

if [ $FACTORY -eq 1 ];then
	factoryDefault
else
	installUpgrade
fi


echo
echo "SUCCESS!"
echo "Astrid Mini Display Successfully Installed/Updated"

if [ $AUTO -eq 0 ];then
	echo "Press <Return> To Continue"
	read line
fi
exit 0
