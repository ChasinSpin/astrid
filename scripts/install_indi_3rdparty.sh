#!/bin/sh

PACKAGES="indi-aok libasi indi-asi libastroasis indi-astroasis indi-avalon indi-armadillo-platypus indi-astrolink4 indi-astromechfoc indi-bresserexos2 indi-celestronaux indi-dreamfocuser indi-eqmod libfli indi-fli indi-starbook-ten"
INDI_FOLDER=/home/pi/indi-3rdparty-2.0.3

cd
/usr/bin/wget https://github.com/indilib/indi-3rdparty/archive/refs/tags/v2.0.3.tar.gz
/usr/bin/mv v2.0.3.tar.gz indi-3rdpartyv2.0.3.tar.gz
/usr/bin/tar -xvzf indi-3rdpartyv2.0.3.tar.gz

/usr/bin/mkdir $INDI_FOLDER/build

for PACKAGE in $PACKAGES
do
	echo "Building: $PACKAGE"
	/usr/bin/mkdir $INDI_FOLDER/build/$PACKAGE
	cd $INDI_FOLDER/build/$PACKAGE

	/usr/bin/cmake -DCMAKE_INSTALL_PREFIX=/usr . ../../$PACKAGE
	if [ $? != 0 ];then
		exit 1
	fi

	/usr/bin/sudo make install
	if [ $? != 0 ];then
		exit 1
	fi

	echo
	echo
	echo
	echo
	echo
	echo
done

rm -rf "$INDI_FOLDER" "/home/pi/indi-3rdpartyv2.0.3.tar.gz"

exit 0
