# Platesolver

## Introduction

Good fast plate solving is a benefit to astrophotography and occultations.  

Sometimes getting that first plate solve can be difficult due to the number of unknowns with a new setup.  Astrid uses "Offline" plate solving using selected star catalogs stored locally and is tuned to plate solve faster for a specified configuration.  If you are unable to plate solve, we suggest using the saved image and uploading it to Astrometry.net's online solver to determine the focal length and index files used, so that you can use these as a starting point, [see Astrometry Online Solving](#astrometry-online-solving)

Generally, Plate Solving requires the following and any of these can prevent
a plate solve:

* [Good Focus](#good-focus)
* [Clear Sky](#clear-sky)
* [Correct Exposure](#correct-exposure)
* [Correct Astrometry Indexes](#correct-astrometry-indexes)
* [Telescope Within Search Radius](#telescope-within-search-radius)
* [Correct Focal Length](#correct-focal-length)
* [Good Optics](#good-optics)

A full sky plate solve will take longer than one within a 5-degree radius of an expected position.  A plate solve will work from the widest field of views to the smallest (yes even Dobsonians and larger SCTs) provided the correct index files are used.

##### If you have plate solving configured correctly you should expect it to take from between 3-5 seconds for a non-full sky solve, and 5-10 seconds for a full sky solve.  If plate solving is taking 30s or more, the chances of getting a solve are unlikely, and you should look into the requirements above.


## Good Focus

Blurred stars distribute the energy of the star over more pixels and reduce the Signal To Noise, this means that the plate solver may not detect the blurred star as a star, and the best case requires longer exposure times.

A Tri-Bahtinov mask provides the best focus, but it is also possible to hand-adjust the focus to a minimum star diameter or use auto-focus.

## Clear Sky

Thin clouds and clouds will prevent plate solving. Sometimes (in the case of thin clouds), it may be possible to expose longer and still get a plate solve.  Also, cloud tends to be variable, you might get a plate solve, and then not later because more cloud has moved in.

Sometimes the brighter background of the cloud can make it more difficult to plate solve due to decreased contrast with the stars.

Thin forest fire smoke (even smoke you can't see through with your own eyes), is transparent to Infrared provided there are no clouds behind it.  The cameras are sensitive to infrared, so you can often get a plate solve in these circumstances.  However, the brighter background can also reduce contrast too with the stars.

## Correct Exposure

The correct exposure has to be selected for plate solving.  Too short an exposure results in too few stars being detected above the background.  If you don't have perfect polar alignment (German Equatorial Mount, Fork Mount on a Wedge, etc.) or are AltAz mounted, then there may be drift on longer exposures, resulting in stars being distorted into short lines and the plate solver failing.

Light pollution or anything that brightens the background in comparison to the stars may also need a longer exposure time.

Generally, we've found that exposures in the 1-5 second range are best.

## Correct Astrometry Indexes

##### Note: Downloading index files will eventually be handled from the User Interface.  Currently, these must be downloaded manually.

Astrometry needs star catalogs to solve for patterns of stars in your images.  These catalogs are called Index Files, and they need to be selected based on the focal length of your configuration to achieve a plate solve.

Index files are selected based on the focal length of the configuration.  Smaller focal lengths (say 100mm) use fewer and smaller index files than say 2500mm as fewer stars are required for a solve.

Typically astrometry.net suggest using a field of diameter of 0.3X to 0.5X your actual field of view (width in this case as it's the largest dimension).

This information is summarized in the table below, lookup your Field Of View Width (convert to arc minutes if necessary) on the left, and download the index series suggested on the right.

| Your Field of View Width (arcmin) | Suggested Index Field Of View Diameter (arcmin) | Index Scale | Index Series | 
| ------------------ | ------------------------------- | ----- | ------ |
| 0.0...6.25 | 2.0...2.8 | 0 | index\-5200\-\*.fits |
| 6.25...10.0 | 2.8...4.0 | 1 | index\-5201\-\*.fits |
| 10.0...14.0 | 4.0...5.6 | 2 | index\-5202\-\*.fits |
| 14.0...20.0 | 5.6...8.0 | 3 | index\-5203\-\*.fits |
| 20.0...27.5 | 8...11 | 4 | index\-5204\-\*.fits |
| 27.5...40.0 | 11...16 | 5 | index\-5205\-\*.fits |
| 40.0...55.0 | 16...22 | 6 | index\-5206\-\*.fits |
| 55.0...5000.0| 22...2000 | 7-19 | 4100 series |

The series can be downloaded here:
	
* 4100 series: [http://data.astrometry.net/4100/](http://data.astrometry.net/4100/)
	* Download index\-4107.fits to index\-4119.fits and place them in folder /media/pi/ASTRID/astrometry/4100
* 5200 series: [https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/](https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/LITE/)
	* Download the index files as detailed, e.g. index\-5204\-\*.fits, and place them in folder /media/pi/ASTRID/astrometry/5204 for example


Other index files if needed can be obtained here: [http://data.astrometry.net](http://data.astrometry.net)

[Configuring the indexes in the astrometry.cfg file](Configuration.md)

If you are having problems plate solving, or plate solving sometimes when there are few stars (typically at higher focal lengths), then you may wish to download an index on either side too.  For example, if index-5202 is your suggested index, you may wish to download index-5203 and then possibly 5201 (larger) so that the solver can look at all 3 index series.  As these files for lower-scale indexes are large, and take a long time to search, we recommend you don't do this unless necessary.

References:

* [http://astrometry.net/doc/readme.html](http://astrometry.net/doc/readme.html)
* [https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/](https://portal.nersc.gov/project/cosmo/temp/dstn/index-5200/)
* [https://pypi.org/project/astrometry/](https://pypi.org/project/astrometry/)

## Telescope Within Search Radius

There are two types of plate solve that can be requested, "Full Sky Solve" where it tries to solve for a location anywhere in the sky, and a "Search Radius", where the plate solve is only considered within say 5 deg of the current location of the search.  This is controlled by the "Full Sky Solve" checkbox in Astrid.

If you are unable to get a solve with "Full Sky Solve" unchecked, then your telescope pointing may be off, in which case try a "Full Sky Solve" 

Scope pointing within the search radius from expected RA/DEC (Full Sky Solve will solve for the whole sky)

Search radius can be configured with the "search\_radius\_deg" setting in  [platesolver.json](Configuration.md#platesolver)

## Correct Focal Length

For a plate solve to be achieved, the plate solver needs a search space for the focal lengths it will consider.  Until you achieve a first plate solver, you won't know the exact focal length of your scope.  We suggest that you roughly calculate the focal length in mm's based on your optics and place that value for the "focal\_length" setting in [platesolver.json
](Configuration.md#platesolver) or within the "Choose Config" prompt provided when Astrid launches.

Once you have achieved a plate solve and the exact focal length is known, then the "focal\_length" setting should be updated to match.

Limits for focal length can be configured with the "scale\_low\_factor" and "scale\_high\_factor" settings in  [platesolver.json](Configuration.md#platesolver), although it's recommended these are left at the defaults of 0.1 and 1.25 respectively and "focal\_length" is amended instead.

Focal length is searched by the plate solver between:

* scale\_low\_factor x focal_length *and*
* scale\_high\_factor x focal_length

## Good Optics

Poor optics can prevent plate solving.  This would be typically lens configurations that significantly change the distance between the stars in differing amounts across the field of view or that distort stars such that they are no longer round.

Generally, it has to be quite severe for it to prevent plate solving, but if you can see distorted stars or the field of view is essentially curved, that would be something to look into.

## Astrometry Online Solving

Astrometry.net provides an online service where you can upload an image plate solve it.  If you are having issues determining plate solving focal length and the best index files to use, we suggest uploading your fits file to:

[https://nova.astrometry.net](https://nova.astrometry.net)

Expand Advanced settings, and check "Source Extractor".  If you have a high focal length (Large SCT, Dobsonian etc.), you may also want to try "Scale" set to "tiny" or "custom" to restrict the search range.

When you have a plate solve (which may take some time), look for the line which says "Field 1: solved with index index-4111.fits" and note the index file used for the solve, in this case "index-4111.fits".

To determine focal length, click on "Go to the results page" and look for the "Pixel Scale" (this should be in arcsec/pixel, if not, convert to arcsec/pixel).

* camera\_pixel\_Size (um): 3.45
	* IMX296 Mono/GSC = 3.45

* pixel_scale (arcsec): 8.63
	* Obtained from astrometry.net plate solve

Focal Length Formula:

	focal_length = 206.265 *  camera_pixel_size / pixel_scale
	focal_length = 206.265 * 3.45 / 8.63
	focal_length = 82.5mm