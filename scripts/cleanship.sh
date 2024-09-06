#!/bin/sh
echo "Clean Astrid to make it ready to ship (includes removing home Wifi, and reenabling privacy notice)"
echo "** Astrid will AUTOMATICALLY POWER DOWN after completion **"
echo -n "Proceed? (y/n) > "
read line
if [ "$line" = "y" -o "$line" = "Y" ]; then
	echo -n "Cleaning..."

	TMP_FILE=/tmp/cleanship.$$

	if [ -d /media/pi/ASTRID ];then
		HIDDEN=/media/pi/ASTRID/configs/hidden.json
		/usr/bin/grep -v "privacy_notice" $HIDDEN > "$TMP_FILE"
		/usr/bin/cat "$TMP_FILE" > $HIDDEN
	fi

	/usr/bin/rm /home/pi/.bash_history

/usr/bin/cat << EOF >$TMP_FILE
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

EOF

	sudo sh -c "/usr/bin/cat $TMP_FILE > /etc/wpa_supplicant/wpa_supplicant.conf"
	/usr/bin/rm $TMP_FILE

	echo Done

	echo
	echo "Powering down now, please wait 15 seconds before removing power..."
	sudo poweroff
fi

exit 0
