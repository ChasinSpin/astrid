#!/bin/bash

GRACE_PERIOD=10

echo "Shutting down in $GRACE_PERIOD seconds..."
echo
echo "** Press any key to prevent shutdown **"
echo

count=$GRACE_PERIOD

while true
do
	echo "Shutting down in $count seconds..."
	read -t 1 -N 1 -r -s ch

	if [ ! -z "$ch" ];then
		echo
		echo "Aborting shutdown..."
		exit 0
	fi

	count=`expr "$count" - 1`

	if [ $count -le 0 ];then
		break
	fi
done

echo
echo "Shutting down..."
echo
echo "** WAIT 15 SECONDS BEFORE REMOVING POWER **"
echo
sleep 1

sudo poweroff

exit 0
