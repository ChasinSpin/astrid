# Settings and Calibration For Occultations

* [Introduction](#introduction)
* [Summary](#summary)
* [FPS](#fps)
* [Gain](#gain)
* [SNR/DNR](#snr/dnr)
* [Darks](#darks)
* [Flats](#flats)
* [Bias](#bias)
* [Binning](#binning)


## Introduction

One of the most common queries among amateur astronomers and astrophotographers is: what settings do I need to record an occultation?   This is a crucial and intricate topic, as it involves a multitude of noise sources and signal-processing techniques. It's important to note that the techniques used for Astrophotography (Pretty Pictures) and Occultations are distinct. When it comes to occultations, our primary focus is on the data and the end result rather than aesthetic appeal.

An OTE tool does the heavy lifting for occultation analysis. My experience is with PyMovie and Pyote, and I haven't verified other tools in terms of the information here.

Also, this information is primarily for recent Digital CMOS sensors, like Astrid. Other sensor types or very old sensors, including analog sensors, may have different considerations.

This is my opinion, and the opinions of some others in the occultation community differ; where I have seen debate in the past, I back up the following with real-life examples and rationale. If you disagree, I encourage you to repeat the experiments and verify for yourself.

It also may not apply to every scenario. For example, an occultation campaign may specify the lowest SNR value, or they may be measuring something different than when a star disappears and reappears.  I.E. They may have other considerations for requesting certain requirements.

Signal-to-noise ratio(SNR) can often mean different things, depends on the source of the noise and the signal. Also, Pyote now has DNR (Drop-To-Noise Ratio).  SNR always refers to the context in which it's being used.

Finally, this guidance is for Occultations only. Astrid is capable of regular astrophotography, and you should use regular techniques (darks, flats, bias) when doing so.

## Summary

In short, record as follows Astrid:

### Gain = 16

...unless the star is so bright it's above the orange line in Exposure Analysis, in which case reduce gain to avoid saturation of the star due to scintillation.

### FPS as fast as you can

For the magnitude of the target, you need the purple line above the cyan background line in Exposure Analysis (where it starts to curve upwards).

Faster frame rates maximize your chances of discovering a Binary Asteroid or Binary Star.  However, you need to balance this with being able to detect the star in the analysis.

In practice, one easy test for this is to see if you can see a star of similar magnitude in video mode when stretched. If you can, it will work; if you can't, decrease the fps until you can.

### Don't sweat DNR/SNR

You're good if your green bar in Pyote is to the right of all 3 red bars.  Maximizing DNR/SNR by increasing exposure is a zero-sum approach and not needed.

However, you should add 6 or 12 static apertures on the target in Pymovie of varying radiuses, and then select the one that gives you the highest DNR/SNR for the event in Pymovie instead.

### You don't need calibration frames

There's no need for Darks, Flats or Bias frames.

### Keep your optics clean

Enough said!

## FPS

**EXAMPLE GOES HERE**

## Gain

Quantization error.
**EXAMPLE GOES HERE (divide pixels by 10 to demonstrate impact on results, reduce color indexes number to show color pixelated image)**

## SNR/DNR

DNR (Drop To Noise), commonly referred to (and historically) as SNR (Signal To Noise), refers to the signal level of the occultation compared to the noise level when the star is not occulted.  It's a measure of the quality of the observation. This should not be confused with the SNR of the star (i.e. the image).

A better DNR does not equate to more accurate timing.  The disappearance and reappearance times and the +/- error bars associated with them, as well as the magnitude drop, remain the same regardless of the DNR.  This is because DNR improves with the square root of exposure, and timing accuracy varies with the square root of exposure. They cancel each other out, so therefore despite seeing a better DNR with a longer exposure, there is no gain to timing accuracy. This makes sense when you consider that the total information from the camera being input into the analysis software is the same regardless of the exposure time.

It's pointless to try to maximize DNR by increasing exposure, nothing is gained.  Provided you have enough DNR to statistically recognize an event and the green bar in Pyote is past the 3 red bars, then you have enough DNR.

**EXAMPLE GOES HERE**


## Darks

It is not necessary to take dark frames to calibrate occultations, here's why:

The Astrid sensor and most modern CMOS sensors have low dark current.  For Astrid, this is 3.2 electrons per pixel per second @ 25C.  In comparison, the readout noise for the sensor is 2.2 electrons.  Both of these are far below the typical [shot noise](https://skyandtelescope.org/astronomy-blogs/astrophotography-signals-noise/#:~:text=Shot%20noise%20comes%20from%20the,in%20otherwise%20smooth%2Dtoned%20areas.) you see in the sky.

Dark current is proportional to the exposure time. At 10 frames per second, dark current noise is 3.2/10 = 0.32 electrons, which is minuscule in relation to the readout noise (which is already minuscule) and the shot noise. Also, darks add processing time during the analysis.

For Occultations, we just don't need darks.


## Flats

Flat frames measure the variable transmittance of the optical system across the field of view.  This can vary due to lenses, mirrors, vignetting etc.

There are a few reasons why taking flat frames is not needed:

* The sensor in Astrid is small and covers a small central area of the telescope's field of view.  This is the area over which there is little vignetting anyway, which is the main reason for flat fielding.
* The scale of any flat correction needed is far below the mag drop you see on the majority of occultations.
* Unless your mount is not tracking, the star remains in the same place in the frame, i.e. it's not varying due to different transmittance as it moves across the FOV.
* Flat Field variations typically are just not that much.  They tend to show up on pretty picture stacking due to the algorithms used, stretching, and the low signal-to-noise ratio of Deep Space Objects(DSO).  However, with occultations, this is less of a consideration.

Reasons why they may **sometimes** be needed are:

* Comparing magnitudes to other stars in the field, however, the flat field would need to be particular bad and the detection requirements high.  This would be more likely to apply to exoplanet transits than occultations.
* The cleanliness of your optics is very poor.

*If you can't see it on the image, you don't need to correct for it.*

Suggestion: Use some of the time it would have taken to acquire flat frames to keep your sensors and optics clean.  Defined dark spots on the image are generally dust on the sensor, clean it and keep it clean by capping or leaving the IOTA focal reducer on.  Less defined dark spots (i.e. defocused) are generally heavy dirt on the telescope optics/lenses and cause less of an issue.


## Bias

Bias Frames can be thought of as the default value of each frame that's read out from a camera when it's dark at the shortest exposure possible.  It represents the offset of a particular pixel (the pedestal).  An ideal camera sensor would have the same offset for each pixel, but in reality, there are manufacturing variances between each individual pixel leading to typically 1 or 2 count variances, plus or minus the average value.

Bias correction is not necessary; the signal of the star is above the bias anyway. Otherwise, you couldn't analyze it, and accounting for the variance is handled by PyMovie in the analysis automatically by the statistical processes involved.  Also, bias varies from frame to frame for video.

Some poor sensors may benefit from a bias frame, but most modern sensors do not need it where the signal is strong, as it is for occultations.


## Binning

Binning is the process of averaging pixels, and it has different impacts depending on whether you are using a CCD or CMOS (Astrid) sensor.

A CCD sensor creates a superpixel when binned.  So, for example, a 2x2 binned CCD will combine 4 pixels into a superpixel.  This superpixel accumulates charge quicker (at the expense of resolution) and only has one readout noise as opposed to 4 readout noises with individual pixels. Hence the Signal-To-Noise Ratio (SNR) is higher binned than unbinned.  CCD cameras have higher readout noise than CMOS.

However, most sensors today are CMOS sensors (as is Astrid), they have a different architecture and don't bin at the pixel level. This means that every pixel read out from a CMOS sensor is unbinned, and binning happens in software (either in the camera itself or in external software). The read noise on CMOS sensors is considerably lower than CCD, and although a 2x2 software bin with CMOS sensor data would result in 4 x readout noises, the total of that is still considerably less than a CCD sensor due to the low readout noise of CMOS.

Binning on CMOS still improves the image's SNR as it averages pixels. So, if you compare two images, binned and unbinned, you'll be able to see stars in the binned that weren't visible in the unbinned. However, due to the math employed in the OTE analysis and the radius around the star, it doesn't change the timing or accuracy of the result.

There may be some outside considerations where the size of the star on the camera and the telescope are mismatched, so you can get better performance/analysis with binning...

However, ordinarily, binning does not provide any advantage to timing or it's accuracy.

**EXAMPLE GOES HERE**





