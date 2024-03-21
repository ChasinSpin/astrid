# USB Flash Drive Layout

## Introduction

The flash drive is used to store astrometry files, images taken, log files, and video.  Because the video is written raw, high throughput is critical, and a regular USB flash drive will not be fast enough.

Never remove the flash drive without shutting down Astrid first.

Suggested Flash Drives:


* [Recommended USB Thumb Drive](USBDriveRequirements.md)
* [Corsair Flash Voyager GTX 128GB USB 3.1 Flash Drive](https://www.amazon.com/Corsair-Flash-Voyager-128GB-Premium/dp/B079NVJPKV)
* [Arcanite 256GB USB 3.1 Flash Drive](https://www.amazon.com/dp/B07RT1WMFB)


## Flash Drive Creation

### Assisted Method

This is the easiest way to format the USB Flash Drive and install the required files:

On the Astrid Desktop, double tap(or double click) "Format USB Flash Drive"

### Manual Method

If for some reason you are enable to use the Assisted Method above, the required format and file structure can also be created as follows:

**IMPORTANT:** The USB flash drive must be formatted **ExFAT** and the volume label must be **ASTRID** for the drive to be recognized.

After formatting, unzip the following into the root of the USB drive:

[AstridUSBFlashDrive.zip](../AstridUSBFlashDrive.zip)

After extraction, you will need to place the folders Photos/configs/astrometry/OTEVideo/TestPlateSolveImages in the root of the USB drive.


## Configs

Please add any needed telescope configurations in the configs folder.  Currently, these have to be entered manually in the .json files.

