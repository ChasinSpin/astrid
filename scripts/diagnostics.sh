#!/bin/sh


ASTRID_DRIVE="/media/pi/ASTRID"
IOZONE_TMP="/tmp/iozone.$$"
OUTPUT_FILE="$ASTRID_DRIVE/diagnostics.txt"


slowExit()
{
	echo "Press <Return> To Exit"
	read line
	exit 2
}

authorize()
{
	echo "IMPORTANT: This utility tests Astrid and the Astrid USB Flash Drive for performance" 
	echo
	echo "It uses a bit of space on the drive, but does not corrupt the drive"
	echo "THIS TEST WILL TAKE A LONG TIME TO RUN, AND TESTS THE DRIVE 6 TIMES"

	echo -n "Do you wish to continue (Y/N): "
	read line
	if [ "$line" != "Y" -a "$line" != "y" ];then
		echo "Aborting...."
		slowExit
	fi
}


astridUsbSummary()
{
	DEVICE=`/usr/bin/lsusb -t | /usr/bin/grep 'Class=Mass Storage'`
	LC=`echo "$DEVICE" | /usr/bin/wc -l`
	if [ "$LC" -lt 1 ];then
		echo "No Mass Storage Devices Found"
	elif [ "$LC" -gt 1 ];then
		echo "Multiple Mass Storage Devices Found"
	else
		DRIVER='UNKNOWN'
		TMP=`echo "$DEVICE" | /usr/bin/grep 'Driver=uas'`
		if [ ! -z "$TMP" ];then
			DRIVER="UASP"
		fi
		TMP=`echo "$DEVICE" | /usr/bin/grep 'Driver=usb-storage'`
		if [ ! -z "$TMP" ];then
			DRIVER="BOT"
		fi

		SPEED='UNKNOWN'
		TMP=`echo "$DEVICE" | /usr/bin/grep '5000M'`
		if [ ! -z "$TMP" ];then
			SPEED="USB3"
		fi

		TMP=`echo "$DEVICE" | /usr/bin/grep '480M'`
		if [ ! -z "$TMP" ];then
			SPEED="USB2"
		fi


		echo "DRIVER: $DRIVER"
		echo "SPEED: $SPEED"
	fi

	echo
	if [ "$DRIVER" != "UASP" -o "$SPEED" != "USB3" ];then
		echo "**** WARNING: NOT UASP OR USB3: THE ASTRID USB DRIVE MAY NOT BE CAPABLE OF FRAME RATES ABOVE 10 FRAMES PER SECOND ****"
	fi
}



report()
{
	echo "CMD: lsusb"
	/usr/bin/lsusb
	echo
	sleep 2

	echo "CMD: lsusb -t"
	/usr/bin/lsusb -t
	echo
	sleep 2

	echo "CMD: lsusb -v"
	/usr/bin/lsusb -v
	echo
	sleep 2

	echo "CMD: usb-devices"
	/usr/bin/usb-devices
	echo
	sleep 2

	echo "CMD: dmesg"
	/usr/bin/dmesg
	echo
	sleep 2

	echo "CMD: hostnamectl"
	/usr/bin/hostnamectl
	echo
	sleep 2

	echo "CMD: rpi-eeprom-update"
	/usr/bin/rpi-eeprom-update
	echo
	sleep 2

	echo "CMD: cat /proc/version"
	/usr/bin/cat /proc/version
	echo
	sleep 2

	echo "CMD: cat ~/astrid/version.txt"
	/usr/bin/cat ~/astrid/version.txt
	echo
	sleep 2

	echo "CMD: mount"
	/usr/bin/mount
	echo
	sleep 2

	echo "CMD: df -Bm"
	/usr/bin/df -Bm
	echo
	sleep 2

	echo "CMD: lsscsi --size"
	/usr/bin/lsscsi --size
	echo
	sleep 2

	echo "CMD: lsscsi --transport"
	/usr/bin/lsscsi --transport
	echo
	sleep 2

	echo "CMDx6: iozone -e -I -a -s 100M -r 4k -r 512k -r 2M -r 16M -i 0 -i 1 -i 2 -f /media/pi/ASTRID/iozone.test"
	FLAG_SLOW=
	count=6
	for i in $(seq $count)
	do
		~/astrid/iozone3_506/bin/iozone -e -I -a -s 100M -r 4k -r 512k -r 2M -r 16M -i 0 -i 1 -i 2 -f $ASTRID_DRIVE/iozone.test | /usr/bin/tee "$IOZONE_TMP"
		TWOMB_LINE=`/usr/bin/grep "^          102400    2048" "$IOZONE_TMP" | /usr/bin/tr -s " "`
		WRITE_SEQUENTIAL=`echo "$TWOMB_LINE" | /usr/bin/cut -f4 -d ' '`
		WRITE_RANDOM=`echo "$TWOMB_LINE" | /usr/bin/cut -f9 -d ' '`

		if [ "$WRITE_SEQUENTIAL" -lt 60000 -o "$WRITE_RANDOM" -lt 60000 ];then
			FLAG_SLOW="Y"
		fi
	done

	/usr/bin/rm "$IOZONE_TMP"


	echo
	astridUsbSummary

	if [ "$FLAG_SLOW" = "Y" ];then
		echo "**** WARNING: TOO SLOW < 60MB/s: THE ASTRID USB DRIVE MAY NOT BE CAPABLE OF FRAME RATES ABOVE 10 FRAMES PER SECOND ****"
	fi
}



authorize

report | /usr/bin/tee "$OUTPUT_FILE"

echo
echo "Finished.  The results have been stored in the file $OUTPUT_FILE on the Astrid USB Drive, press <Return> when ready"
read line

exit 0
