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

### Recommended Drives:

| Drive |  WT pSLC | WT No pSLC | pSLC | UASP | Recommended |
| ----- | ------- | ---------- | ---- | ---- | ----------- |
| [Reletch Elite7 Pro USB 3.2 Solid State Drive Read 480MB/s 256GB](https://www.aliexpress.us/item/1005006081674212.html) | 87.78MB/s | 87.78MB/s | - | No | Likely best choice, only 1 sampled.
| [Corsair Flash Voyager GTX 128GB USB 3.1 Flash Drive](https://www.amazon.com/Corsair-Flash-Voyager-128GB-Premium/dp/B079NVJPKV) (also 256GB version of this drive) | ~100MB/s | ~46MB/s | ~4.2GB | Yes | Yes (but only upto 4GB videos) |
| [TOPESEL 256GB USB 3.1 Gen 2 Flash Drive Super Speed 400Mb/s](https://www.aliexpress.us/item/1005003422090205.html) | 83.9MB/s | 83.9MB/s | None | No | Some other TOPESEL drives have been inconsistent, and they don't give refunds, only one of this model has been sampled. |
| [Patroit Supersonic Rage Prime USB 3.2 Gen 2 Flash Drive - 500GB PEF500GRPMW32U](https://www.amazon.com/Patriot-Supersonic-Prime-Flash-Drive/dp/B095HXK1D1) | 98.77MB/s | 87.49MB/s | Unknown but >10GB | - | Yes |

### Avoid:

| Drive | WT pSLC | WT No pSLC | pSLC | UASP | Recommended |
| ----- | ------- | ---------- | ---- | ---- | ----------- |
| Lexar 128GB JumpDrive P30 USB 3.2 Gen 1 Flash Drive (LJDP030128G-RNQNG) | ~90MB/s | ~50MB/s | ~12GB | Yes | Avoid (unpredictable) speeds, start off around 8MB/s) |
| Arcanite 256GB USB 3.1 Flash Drive AK58256G | - | - | ~3GB | Yes | Avoid (slow, cache burnt through fast) |
| Sandisk Extreme Pro 3.2 | - | - | ~ >100GB | No | Avoid (unpredictable speed/features/faulty drives) |
| [TOPESEL 256GB USB 3.1 Gen 2 High Speed Thumb Drive](https://www.aliexpress.us/item/1005005393760142.html) | 55MB/s | 55MB/s | - | No | Avoid, doesn't meet specs, TOPESEL won't refund |
| [TOPESEL 128GB USB 3.1 Flash Drive, Up to 380MB/s](https://www.amazon.ca/dp/B08QTXBG9H) | ~98MB/s | ~70MB/s | ~3GB | No | Meets 30fps just on some sample, others fail dramatically.  Avoid. |

Reference: [Fastest USB flash drive benchmark test 2024](https://ssd-tester.com/usb_flash_drive_test.php)


## Fragmentation

Deleting files from a USB Drive may fragment the drive and, depending on its quality, slow down the speed at which data can be written.  This effect can vary depending on the drive and how it's designed.

## Speed Testing 

Use the Diagnostics icon on the desktop in "Astrid Tools" to run a speed test.  The results are placed in diagnostics.txt on the Astrid drive.