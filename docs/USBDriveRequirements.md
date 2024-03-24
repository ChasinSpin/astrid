# USB Drive Requirements

## Astrid Requirements

Astrid writes frames that are 2MB in size.  This means that at 30fps, Astrid will write data to the USB Drive at 60MB/s.

Astrid contains a cache that is 160 frames in size, but if the USB Drive is poorly implemented or not up to the requirements, then eventually frames will be dropped.

## USB Drive

To keep up with the large raw video files and high frame rates Astrid uses, an appropriate USB Drive must be selected.  The requirements are as follows:

* USB 3.0, ideally 3.1 or 3.2
* More than 120MB/s write speed continuously (random and sequential).  These need to be in real-life situations, not just advertised, they must also persist when there's no more caching available.
* UASP support (up to 50% speed increase)
* Sufficient size to store the files
* Plugged into the Blue USB ports on the Raspberry Pi
* Always formatted in Astrid

## pSLC Cache

Most drives have pSLC cache. This can exhibit some unusual effects. For example, a drive can be writing at, say, 100-1000MB/s and then, after a certain amount has been transferred, drop down to 10-40MB/s (which no longer meets Astrid's requirements). The drive may not be back up to full speed for even as long as 30 minutes or write a smaller amount faster and then slow down again.

References:

[pSLC Cache Design for Enhanced Performance and Lifetime](https://www.flashmemorysummit.com/Proceedings2019/08-06-Tuesday/20190806_EMBD-101A-1_McCormick.pdf)
[Fastest USB flash drive benchmark test 2024](https://ssd-tester.com/usb_flash_drive_test.php)

## USB Thumb Drive Testing

| Drive | Min Sequential Write 2MB | Min Random Write 2MB | WT pSLC | WT No pSLC | pSLC | UASP | Recommended |
| ----- | ------------------------ | -------------------- | ------- | ---------- | ---- | ---- | ----------- |
| Corsair Flash Voyager GTX 128GB USB 3.1 | 113.4MB/s | 172.8MB/s | ~100MB/s | ~46MB/s | ~4.2GB | Yes | Yes (but only upto 4GB videos) |
| Lexar 128GB JumpDrive P30 USB 3.2 Gen 1 Flash Drive (LJDP030128G-RNQNG) | 57.7MB/s | 91.6MB/s | ~90MB/s | ~50MB/s | ~12GB | Yes | Avoid (unpredictable speeds, start off around 8MB/s) |
| TOPESEL 128GB USB 3.1 Flash Drive | 107.8 | 240.4 | ~98MB/s | ~70MB/s | ~3GB | No | Meets 30fps just, but is consistant |
| Sandisk Extreme Pro 3.2 | 21.5MB/s | 8.9MB/s | - | - | ~ >100GB | No | Avoid (unpredictable speed/features/fault drives) |
| Arcanite 256GB USB 3.1 Flash Drive AK58256G | 24MB/s | 30MB/s | - | - | ~3GB | Yes | Avoid (slow, cache burnt through fast) |

Reference: [Fastest USB flash drive benchmark test 2024](https://ssd-tester.com/usb_flash_drive_test.php)


## Fragmentation

Deleting files from a USB Drive may fragment the drive and, depending on its quality, slow down the speed at which data can be written.  This effect can vary depending on the drive and how it's designed.

## Speed Testing 

Use the Diagnostics icon on the desktop to run a speed test.  The results are placed in diagnostics.txt on the Astrid drive.

## UASP mode and USB 3.0

See "Speed Testing" above.

More information:

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





