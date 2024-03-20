#!/bin/sh

astridUsbSummary()
{
	DEVICE=`/usr/bin/lsusb -t | /usr/bin/grep 'Class=Mass Storage'`
	LC=`echo "$DEVICE" | /usr/bin/head -1`

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

	echo "DRIVER=$DRIVER"
	echo "SPEED=$SPEED"
}



astridUsbSummary

exit 0
