#!/bin/sh

echo "Configuring lightsout..."

LIGHTSOUT_CONFIG="/home/pi/.astrid_lightsout"

if [ -f "$LIGHTSOUT_CONFIG" ];then
	. "$LIGHTSOUT_CONFIG"
else
	PILEDS=1
	ETHLEDS=1
fi

if [ "$PILEDS" = 1 ];then
	echo "Enabling Power/Activity LEDs"
	echo "(Handled automatically after reboot)"
else
	echo "Disabling Power/Activity LEDs"
	sudo sh -c "echo 0 > /sys/class/leds/ACT/brightness"
	sudo sh -c "echo 0 > /sys/class/leds/PWR/brightness"
fi

if [ "$ETHLEDS" = 1 ];then
	echo "Enabling Ethernet LEDs"
	echo "(Handled automatically after reboot or network change)"
else
	echo "Disabling Ethernet LEDs"
	sudo /usr/local/bin/mdio-tool w eth0 0x17 0x0f04
	sudo /usr/local/bin/mdio-tool w eth0 0x15 0x044
fi

exit 0
