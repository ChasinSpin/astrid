#!/bin/sh


extractLine()
{
	RET=`echo "$1" | /usr/bin/grep "$2" | /usr/bin/sed "s/$2//"`
	echo "$RET"
}



astridDriveSummary()
{
	DRIVE="$1"

	DEV_DEVICE=`/usr/bin/mount | /usr/bin/grep "$DRIVE" | cut -f1 -d" "`
	if [ -z "$DEV_DEVICE" ];then
		echo "ERROR=$DRIVE Not Mounted"
		return 1
	fi

	#TMP=`/usr/bin/udevadm info --attribute-walk "$DEV_DEVICE"`
	#USB_MANUFACTURER=`extractLine "$TMP" '    ATTRS{manufacturer}=="'`
	#USB_PRODUCT=`extractLine "$TMP" '    ATTRS{product}=="'`

	TMP=`/usr/bin/udevadm info --query=all -n "$DEV_DEVICE"`
	ATA_WRITE_CACHE=`extractLine "$TMP" "E: ID_ATA_WRITE_CACHE="`
	ATA_WRITE_CACHE_ENABLED=`extractLine "$TMP" "E: ID_ATA_WRITE_CACHE_ENABLED="`
	ATA_SATA_SIGNAL_RATE_GEN2=`extractLine "$TMP" "E: ID_ATA_SATA_SIGNAL_RATE_GEN2="`
	ATA_SATA_SIGNAL_RATE_GEN1=`extractLine "$TMP" "E: ID_ATA_SATA_SIGNAL_RATE_GEN1="`
	DEVPATH=`extractLine "$TMP" "E: DEVPATH="`
	USBDEVPATH="/sys/"`echo "${DEVPATH}" | /usr/bin/cut -f2-10 -d"/"`

	TMP=`/usr/bin/udevadm info --query=all "$USBDEVPATH"`
	USB_SERIAL=`extractLine "$TMP" "E: ID_SERIAL_SHORT="`
	if [ -z "$USB_SERIAL" ];then
		USBDEVPATH="/sys/"`echo "${DEVPATH}" | /usr/bin/cut -f2-11 -d"/"`
		TMP=`/usr/bin/udevadm info --query=all "$USBDEVPATH"`
		USB_SERIAL=`extractLine "$TMP" "E: ID_SERIAL_SHORT="`
	fi

	USBDEVPATH="/sys/"`echo "${DEVPATH}" | /usr/bin/cut -f2-10 -d"/"`
	USB_MANUFACTURER=`extractLine "$TMP" "E: ID_VENDOR="`
	USB_PRODUCT=`extractLine "$TMP" "E: ID_MODEL_ENC=" | /usr/bin/sed 's/\\\x20/ /g'`
	USB_VENDOR_ID=`extractLine "$TMP" "E: ID_VENDOR_ID="`
	USB_PRODUCT_ID=`extractLine "$TMP" "E: ID_MODEL_ID="`

	SANDISK="NO"
	TMP=`echo "$USB_MANUFACTURER" | /usr/bin/grep -i "sandisk"`
	if [ ! -z "$TMP" ];then
		SANDISK="YES"
	fi
	
	MATCHING_ENTRY=0
	DRIVER="UNKNOWN"
	SPEED="UNKNOWN"
	TMP_FILE="/tmp/astrid-drive-info.$$"
	/usr/bin/usb-devices > "$TMP_FILE"

	while read line
	do
		#echo "$line"

		TMP=`echo "$line" | /usr/bin/grep "^T:  "`
		if [ ! -z "$TMP" ];then
			UD_T="$TMP"
			MATCHING_ENTRY=0
		fi

		TMP=`echo "$line" | /usr/bin/grep "^P:  Vendor=${USB_VENDOR_ID} ProdID=${USB_PRODUCT_ID}"`
		if [ ! -z "$TMP" ];then
			MATCHING_ENTRY=1

			TMP2=`echo "$UD_T" | /usr/bin/grep "Spd=5000"`
			if [ ! -z "$TMP2" ];then
				SPEED="USB3"
			fi

			TMP2=`echo "$UD_T" | /usr/bin/grep "Spd=480"`
			if [ ! -z "$TMP2" ];then
				SPEED="USB2"
			fi
		fi

		TMP=`echo "$line" | /usr/bin/grep "^I:  "`
		if [ ! -z "$TMP" -a $MATCHING_ENTRY = 1 ];then
			TMP2=`echo "$TMP" | /usr/bin/grep "Driver=uas"`
			if [ ! -z "$TMP2" ];then
				DRIVER="UASP"
			fi
			TMP2=`echo "$TMP" | /usr/bin/grep "Driver=usb-storage"`
			if [ ! -z "$TMP2" ];then
				DRIVER="BOT"
			fi

			break
		fi
	done <"$TMP_FILE"
	/usr/bin/rm "$TMP_FILE"
	
	echo "DEV_DEVICE=$DEV_DEVICE"
	echo "USB_MANUFACTURER=$USB_MANUFACTURER"
	echo "USB_PRODUCT=$USB_PRODUCT"
	echo "USB_VENDOR_ID=$USB_VENDOR_ID"
	echo "USB_PRODUCT_ID=$USB_PRODUCT_ID"
	echo "USB_SERIAL=$USB_SERIAL"
	echo "ATA_WRITE_CACHE=$ATA_WRITE_CACHE"
	echo "ATA_WRITE_CACHE_ENABLED=$ATA_WRITE_CACHE_ENABLED"
	echo "ATA_SATA_SIGNAL_RATE_GEN2=$ATA_SATA_SIGNAL_RATE_GEN2"
	echo "ATA_SATA_SIGNAL_RATE_GEN1=$ATA_SATA_SIGNAL_RATE_GEN1"
	echo "DRIVER=$DRIVER"
	echo "SPEED=$SPEED"
	echo "SANDISK=$SANDISK"

	return 0
}



astridDriveSummary /media/pi/ASTRID
if [ $? != 0 ];then
	echo "Aborting..."
	exit 1
fi

exit 0
