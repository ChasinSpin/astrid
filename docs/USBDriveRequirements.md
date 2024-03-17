# USB Drive Requirements

## Astrid Requirements

Astrid writes frames that are 2MB in size.  This means that at 30fps, Astrid will write data to the USB Drive at 60MB/s.

Astrid contains a cache that is 160 frames in size, but if the USB Drive is poorly implemented or not up to the requirements, then eventually frames will be dropped.

## USB Drive

To keep up with the large raw video files and high frame rates Astrid uses, an appropriate USB Drive must be selected.  The requirements are as follows:

* USB 3.0, ideally 3.2
* More than 120MB/s write speed continuously (random and sequential).  These need to be in real-life situations, not just advertised
* UASP support
* Sufficient size to store the files
* Plugged into the Blue USB ports on the Raspberry Pi
* Always format in Astrid

## Corsair Flash Voyager GTX 128GB USB 3.1

This works well at 30fps and supports UASP mode.

Testing:

| Write Type | Test Examples |
| ---------- | ------------- |
| Sequential | 133MB/s, 124MB/s,  111MB/s, 125MB/s, 128MB/s, 127MB/s |
| Random | 310MB/s, 310MB/s, 312MB/s, 243MB/s, 311MB/s, 310MB/s |

## Sandisk Extreme Pro 3.2

This drive has been demonstrated to run no faster than 20fps; it does not meet its advertised speeds for sequential or random writes.  It does not negotiate UASP mode.

Testing:

| Write Type | Test Examples |
| ---------- | ------------- |
| Sequential | 78.5MB/s, 27MB/s, 50MB/s, 65MB/s, 34MB/s, 40MB/s |
| Random | 12.6MB/s, 18MB/s, 15MB/s, 14MB/s, 40MB/s, 22MB/s |

It's possible it may work if files are not deleted from it, and it's reformatted often.  Your mileage may vary.

## Fragmentation

Deleting files from a USB Drive may fragment the drive and, depending on its quality, slow down the speed at which data can be written.

## Speed Testing 

### Install iozone
	cd
	wget https://www.iozone.org/src/current/iozone3_506.tar
	tar -xvf iozone3_506.tar
	rm iozone3_506.tar
	cd iozone3_506/src/current
	make linux-arm
	./iozone -e -I -a -s 100M -r 4k -r 512k -r 2M -r 16M -i 0 -i 1 -i 2 -f /media/pi/ASTRID/iozone.test
	
Look at the 2MB size line and write (sequential) and random write (values are in KB/s).  Run a number of times as speeds can vary.

## UASP mode and USB 3.0

Reference: [UASP v. BOT](https://www.jeffgeerling.com/blog/2020/uasp-makes-raspberry-pi-4-disk-io-50-faster)

USB 3 is faster than USB 2, and UASP mode provides a higher speed for both USB 2 and USB 3 than BOT mode.

To determine if a USB Drive is connected via USB 3, type:

	lsusb -t
	
and look for:

	5000M = USB 3
	480M  = USB 2

To determine if a USB Drive is connected via USAP, type:

	lsusb -t
	
and look for:

	Driver=uas 				= UASP
	Driver=usb-storage		= BOT





