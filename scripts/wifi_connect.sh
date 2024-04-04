#!/bin/sh
echo
echo "Connecting to an available network we know about..."
echo
echo "If unable to connect, the Hotspot will be restarted."
echo
echo "** Please check for the Hotspot if you're unable to connect **"
sleep 2
/usr/bin/sudo /usr/bin/autohotspot
exit 0
