#!/bin/sh

ASTRID_FOLDER="/home/pi/astrid"
APP_FOLDER="$ASTRID_FOLDER/app"
OTESTAMPER_FOLDER="$ASTRID_FOLDER/OTEStamper"

echo "Creating desktop icons..."
/usr/bin/rm -f /home/pi/Desktop/AstridApp.desktop
/usr/bin/rm -f /home/pi/Desktop/WifiSetup.desktop
/usr/bin/rm -f /home/pi/Desktop/AstridUpgrade.desktop
/usr/bin/rm -f /home/pi/Desktop/KillAstrid.desktop
/usr/bin/rm -f /home/pi/Desktop/FormatUSBFlashDrive.desktop

/usr/bin/ln -s /home/pi/astrid/desktop/AstridApp.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/WifiSetup.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/AstridUpgrade.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/KillAstrid.desktop /home/pi/Desktop
/usr/bin/ln -s /home/pi/astrid/desktop/FormatUSBFlashDrive.desktop /home/pi/Desktop

echo "Installing ravf..."
pip install --no-deps ravf

echo "Making ospi..."
cd $APP_FOLDER
./make-ospi.sh

echo "Making oteutils..."
cd "$APP_FOLDER"
./make_oteutils.sh

echo "Installing firmware..."
cd "$OTESTAMPER_FOLDER/firmware"
/usr/bin/make clean
/usr/bin/make writefuses
/usr/bin/make install
/usr/bin/make clean

exit 0
