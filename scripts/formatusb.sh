#!/bin/sh

DEVICE_MAIN="/dev/sda"
DEVICE_PART="/dev/sda1"
ASTRID_FOLDER="/media/pi/ASTRID"


slowExit()
{
	echo "Press <Return> To Exit"
	read line
	exit 2
}

authorize()
{
	echo "IMPORTANT: This utility formats a USB Flash Drive and configures it for ASTRID"
	echo
	echo "WARNING: ALL FILES ON THE USB FLASH DRIVE WILL BE DESTROYED!"
	echo "This includes all..."
	echo "    Videos/Photos/Fits"
	echo "    Astrometry Files"
	echo "    Astrid Configurations"
	echo

	echo -n "Do you wish to continue (Y/N): "
	read line
	if [ "$line" != "Y" -a "$line" != "y" ];then
		echo "Aborting...."
		slowExit
	fi

	echo
	echo -n "Is ONLY 1 USB Flash Drive Plugged into Astrid? (Y/N): "
	read line
	if [ "$line" != "Y" -a "$line" != "y" ];then
		echo "Aborting...."
		slowExit
	fi

	echo 
	echo "**** WARNING: FINAL CHANCE ****"
	echo  "IF YOU WISH TO DELETE ALL FILES ON YOUR USB FLASH DRIVE, TYPE:"
	echo  "       ERASE USB DRIVE NOW<Return>"

	read line
	if [ "$line" != "ERASE USB DRIVE NOW" ];then
		echo "Aborting...."
		slowExit
	fi
}



#
# MAIN
#


authorize

# Exclude CIRCUITPY
TMP=`/usr/bin/mount | /usr/bin/grep "CIRCUITPY"`
if [ ! -z "$TMP" ];then
	TMP=`echo "$TMP" | /usr/bin/grep "sda"`
	if [ ! -z "$TMP" ];then
		DEVICE_MAIN="/dev/sdb"
		DEVICE_PART="/dev/sdb1"
	fi
fi

if [ ! -b "$DEVICE_MAIN" ];then
	echo "USB Flash Drive: $DEVICE_MAIN Not Found, drive has not been inserted, aborting..."
	slowExit
fi

echo "USB Flash Drive: $DEVICE_MAIN Found"

if [ -b "$DEVICE_MAIN" -o -b "$DEVICE_PART" ];then
	TMP=`/usr/bin/mount | grep "$DEVICE_MAIN" | /usr/bin/cut -f3 -d" "`
	for mntpoint in "$TMP"
	do
		if [ ! -z "$mntpoint" ];then
			LIST=`/usr/bin/ls -R "$TMP"`
			LIST_COUNT=`echo "$LIST" | /usr/bin/wc -l`
			if [ "$LIST_COUNT" -gt 1 ];then
				echo
				echo "WARNING: Files have been found on the USB Flash Drive"
				echo

				echo "$LIST"
			
				echo
				echo "WARNING: Files have been found on the USB Flash Drive"
				echo -n "PERMANENTLY ERASE ALL THESE FILES? (Y/N): "
				read line
				if [ "$line" != "Y" -a "$line" != "y" ];then
					echo "Aborting...."
					slowExit
				fi
			fi
		fi
	done
	echo "Unmounting USB Drives..."
	/usr/bin/umount "$DEVICE_MAIN" >/dev/null 2>&1
	/usr/bin/umount "$DEVICE_PART" >/dev/null 2>&1
fi

echo "Creating partition table..."

echo 'type=7' | sudo /usr/sbin/sfdisk "$DEVICE_MAIN"
if [ $? != 0 ];then
	echo "ERROR: sfdisk, try removing and inserting USB Flash Drive, aborting..."
	slowExit
fi

echo "Formatting USB Flash Drive as ExFAT..."
sudo /usr/sbin/mkfs -t exfat -L ASTRID "$DEVICE_PART"
if [ $? != 0 ];then
	echo "ERROR: mkfs, aborting..."
	slowExit
fi

echo "Format complete"
sudo /usr/bin/eject "$DEVICE_PART"
sudo /usr/bin/eject "$DEVICE_MAIN"
echo
echo "***************************************************************************"
echo "VERY IMPORTANT: Remove USB Flash Drive and Insert back into Blue USB Socket"
echo "***************************************************************************"
echo
echo "    Note 1: Window will popup when inserted, hit Cancel"
echo "    Note 2: You can safely ignore message about not safely ejecting"
echo "Press <Return> when ready to confirm you have removed and reinserted the USB Flash Drive"
read line

echo
echo "Waiting for drive to come online"
/usr/bin/sleep 5

TMP=`/usr/bin/mount | grep "$DEVICE_PART" | /usr/bin/cut -f3 -d" "`
if [ ! -z "$TMP" -a "$TMP" = "$ASTRID_FOLDER" ];then
	echo "USB Flash Drive Detected"

	echo "Copying ASTRID Files..."
	/usr/bin/unzip ~/astrid/AstridUSBFlashDrive.zip -d "$ASTRID_FOLDER"
	if [ $? != 0 ];then
		echo "ERROR: unzip, aborting..."
		slowExit
	fi

	echo "Moving files to destination..."
	/usr/bin/rm -rf "${ASTRID_FOLDER}/__MACOSX"	
	/usr/bin/mv "${ASTRID_FOLDER}/AstridUSB"/* "$ASTRID_FOLDER"
	/usr/bin/rm -f "${ASTRID_FOLDER}/AstridUSB/.DS_Store"
	/usr/bin/rmdir "${ASTRID_FOLDER}/AstridUSB"	
else
	echo "ERROR: USB Flash Drive Not Detected, ASTRID flash drive format not complete, try again"
	slowExit
fi

echo
echo "SUCCESS!"
echo "Astrid USB Flash Drive Successfully Created"
echo "Press <Return> To Continue"
read line
exit 0
