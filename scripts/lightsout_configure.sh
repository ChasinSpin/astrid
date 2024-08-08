#!/bin/sh



writeConfig()
{
	echo "PILEDS=$PILEDS" > "$LIGHTSOUT_CONFIG"
	echo "ETHLEDS=$ETHLEDS" >> "$LIGHTSOUT_CONFIG"
}



echo "Utility to enable/disable externally visible lights on Astrid."
echo
echo "These changes persist over power cycles, and when lights are switched off you will"
echo "no longer see the statuses of Astrid functionality you require."
echo "Generally it is only recommended to do this if you need zero light output"
echo "for security our light ingress considerations (RASA, Hyperstar, Fastar, Prime Focus)."
echo
echo "After lights out is enabled, lights will still show on boot, but switch off when"
echo "the Astrid app is started"
echo
echo "GPS PPS light cannot be turned off from here, it must be covered with electrical tape."
echo
echo "Please type one of the following numbers and hit <RETURN or ENTER>..."
echo

LIGHTSOUT_CONFIG="/home/pi/.astrid_lightsout"

if [ -f "$LIGHTSOUT_CONFIG" ];then
	. "$LIGHTSOUT_CONFIG"
else
	PILEDS=1
	ETHLEDS=1
	writeConfig
fi

LIGHTSOUT="/home/pi/astrid/scripts/lightsout.sh"


while true
do
	echo
	echo "1 - Disable Power(Red) and Activity(Green) LEDs"
	echo "2 - Disable Ethernet(Green and Yellow) LEDs"
	echo "3 - Enable Power(Red) and Activity(Green) LEDs"
	echo "4 - Enable Ethernet(Green and Yellow) LEDs"
	echo "0 - Exit"

	echo
	echo -n "Enter number above> "
	read line

	#if [ "$line" = 0 -o "$line" = 1 -o "$line" = 2 -o "$line" = 3 -o "$line" = 4 ];then
		case $line in
			1)
				echo "Disabled Power(Red) and Activity(Green) LEDs"
				PILEDS=0
				writeConfig
				$LIGHTSOUT	
				;;	
			2)
				echo "Disabled Ethernet(Green and Yellow) LEDs"
				ETHLEDS=0
				writeConfig
				$LIGHTSOUT	
				;;	
			3)
				echo "Enabled Power(Red) and Activity(Green) LEDs"
				PILEDS=1
				writeConfig
				$LIGHTSOUT	
				echo "**** CHANGE WILL TAKE PLACE AFTER NEXT REBOOT ****"
				;;	
			4)
				echo "Enabled Ethernet(Green and Yellow) LEDs"
				ETHLEDS=1
				writeConfig
				$LIGHTSOUT	
				echo "**** CHANGE WILL TAKE PLACE AFTER NEXT REBOOT OR NETWORK CHANGE ****"
				;;	
			0)
				echo "Exiting..."
				exit 0
				;;
		esac
	#fi
done
exit 0
