#!/bin/sh



# Switch Chromium Hardware Acceleration Off

chromeHardwareAccelerationOff()
{
        CONFIG_FILE="/home/pi/.config/chromium/Local State"

        TMP=`/usr/bin/grep '"hardware_acceleration_mode":{"enabled":true}' "$CONFIG_FILE"`
        if [ ! -z "$TMP" ]; then
                echo "Switching Hardware Acceleration OFF for Chromium"
                /usr/bin/sed 's/\"hardware_acceleration_mode\"\:{\"enabled\"\:true}/\"hardware_acceleration_mode\"\:{\"enabled\"\:false}/' "$CONFIG_FILE" > "$CONFIG_FILE".tmp
                /usr/bin/cat "$CONFIG_FILE".tmp > "$CONFIG_FILE"
                /usr/bin/rm -f "$CONFIG_FILE".tmp
        fi
}



# Switch OS Upgrade Notifications Off

osUpgradeNotificationsOff()
{
	LXDE_PANEL_OLD="/etc/xdg/lxpanel/LXDE-pi/panels/panel"
	LXDE_PANEL_NEW="/home/pi/astrid/install/lxde-panel"

	TMP=`/usr/bin/grep "type=updater" "$LXDE_PANEL_OLD"`
	if [ ! -z "$TMP" ]; then
		echo "Switching OS Upgrade Notifications OFF"
		sudo sh -c "/usr/bin/cat \"$LXDE_PANEL_NEW\" > \"$LXDE_PANEL_OLD\""
	fi
}



ASTRID_FOLDER="/home/pi/astrid"
APP_FOLDER="$ASTRID_FOLDER/app"
OTESTAMPER_FOLDER="$ASTRID_FOLDER/OTEStamper"

echo "Creating desktop icons..."
/usr/bin/rm -f /home/pi/Desktop/AstridApp.desktop
/usr/bin/rm -f /home/pi/Desktop/WifiSetup.desktop
/usr/bin/rm -f /home/pi/Desktop/AstridUpgrade.desktop
/usr/bin/rm -f /home/pi/Desktop/KillAstrid.desktop
/usr/bin/rm -f /home/pi/Desktop/FormatUSBFlashDrive.desktop
/usr/bin/rm -f /home/pi/Desktop/Player.desktop

/usr/bin/ln -s /home/pi/astrid/desktop/AstridApp.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/WifiSetup.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/AstridUpgrade.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/KillAstrid.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/FormatUSBFlashDrive.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/Player.desktop /home/pi/Desktop

echo "Installing ravf..."
pip install --no-deps ravf

echo "Making ospi..."
cd $APP_FOLDER
./make-ospi.sh

echo "Making oteutils..."
cd "$APP_FOLDER"
./make_oteutils.sh

chromeHardwareAccelerationOff
osUpgradeNotificationsOff

echo "Installing firmware..."
cd "$OTESTAMPER_FOLDER/firmware"
/usr/bin/make clean
/usr/bin/make writefuses
/usr/bin/make install
/usr/bin/make clean

exit 0
