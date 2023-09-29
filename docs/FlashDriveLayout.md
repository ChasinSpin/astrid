# USB Flash Drive Layout

## Introduction

The flash drive is used to store astrometry files, images taken, log files, and video.  Because the video is written raw, high throughput is critical, and a regular USB flash drive will not be fast enough.

Never remove the flash drive without shutting down Astrid first.

Suggested Flash Drives:


* [Sandisk 128GB Extreme Pro USB 3.2 SDCZ880-128G-GAM46](https://www.amazon.com/SanDisk-128GB-Extreme-Solid-State/dp/B08GYM5F8G/ref=sr_1_3?crid=3V64CEU0M0KOW&keywords=SanDisk%2B128GB%2BExtreme%2BPRO%2BUSB%2B3.2%2BSolid%2BState%2BFlash%2BDrive%2B-%2BSDCZ880-128G-GAM46&qid=1695578870&sprefix=sandisk%2B128gb%2Bextreme%2Bpro%2Busb%2B3.2%2Bsolid%2Bstate%2Bflash%2Bdrive%2B-%2Bsdcz880-128g-gam46%2Caps%2C237&sr=8-3&th=1)
* [Corsair Flash Voyager GTX 128GB USB 3.1 Flash Drive](https://www.amazon.com/Corsair-Flash-Voyager-128GB-Premium/dp/B079NVJPKV)
* [Arcanite 256GB USB 3.1 Flash Drive](https://www.amazon.com/dp/B07RT1WMFB)

## Formatting

**IMPORTANT:** The USB flash drive must be formatted **ExFAT** and the volume label must be **ASTRID** for the drive to be recognized.

After formatting, unzip the following into the root of the USB drive:

[AstridUSBFlashDrive.zip](../AstridUSBFlashDrive.zip)

After extraction, you will need to place the folders Photos/configs/astrometry/OTEVideo/TestPlateSolveImages in the root of the USB drive.


## Configs

Please add any needed telescope configurations in the configs folder.  Currently, these have to be entered manually in the .json files.

