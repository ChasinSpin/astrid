#!/bin/sh
echo "Clean Astrid to make it ready to ship (includes removing home Wifi)"
echo "** Astrid will AUTOMATICALLY POWER DOWN after completion **"
echo -n "Proceed? (y/n) > "
read line
if [ "$line" = "y" -o "$line" = "Y" ]; then
	echo -n "Cleaning..."
	/usr/bin/rm /home/pi/.bash_history

	TMP_FILE=/tmp/cleanship.$$
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
