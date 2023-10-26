# Build Kit (Skill Level Advanced)

If you are not using the Partial Kit and you are building entirely from scratch, you will need to follow these instructions and then follow the [Assembly Guide](AssemblyGuide.md)

## Tools Required

* Hobby Knife
* Scissors
* Small Pliers
* Phillips Screw Driver (long shaft, thin, shaft diameter max 4mm)
* 2.5mm drill
* Small Soldering Iron and Solder
* Tweezers
* Hot-Glue
* Super-Glue
* Electrical Tape
* Loctite 242

## Parts Required

* [CAM-MIPI296RAW-Trigger](https://www.inno-maker.com/product/cam-mipi296raw-trigger/)
* Flat-Flex Camera Cable (comes with the camera)
* CS Lens Seat (comes with the camera)
* GPS External Antenna and PigTail [Active GPS Antenna with RG178 Pigtail](https://www.amazon.com/Bingfu-Waterproof-Navigation-Adhesive-Receiver/dp/B083D59N55)
* OTEStamper Board
* Small Wire-Wrapping Wire
* Trigger Board Cable 0.1\" header
* GT-U7 GPS
* 5-Pin GPS Header (yellow)
* 2.5mm x 8mm bolt
* 9 x 2.5mm Nut (Black)
* 4 x 2.5mm Nuts (Black)
* 4 x 2.5mm x 10mm Bolts
* 8 x 2.5mm x 14mm Bolts
* 4 x Aluminum or Brass Hex Standoffs Posts (2.5mm x 0.45 x 11mm)
* Small Zip-Tie
* Astrid 3D-Printed:
	* Case Bottom
	* Case Top
	* Camera Cover
	* 4 x Camera Board Mounting Posts
	* GPS Lozenge
	* 2.6mm thick spacer (washer)
	* Power Socket Block
* Raspberry Pi Heatsinks
* Raspberry Pi 30mm x 30mm x 7mm Brushless 5V Fan (100mA max current)

## Camera

*Note: This process is just for now, and will be removed in future with some custom camera boards from the supplier*


* Drill out the 4 PCB mounting holes with a 2.5mm drill.	 
	 
	![Drilling Out PCB Mounting Holes](images/assembly1.jpg)
	 
* Remove any burrs created by the drill with a hobby knife, the board needs to be completely flat to fit the case.
* Clean off any dust from the drilling.
* Desolder J2 and J3 if they are present.
* Cut the tracks to J3 so that it is isolated from the rest of the circuitry.

	![Cut the tracks to J3](images/assembly2.jpg)

* Solder a right angled 0.1\" header where J3 was

	![Solder Right Angled Header](images/assembly3.jpg)
	
* Clip the unused pin on the header and shown and pre-tin (blob of solder) on the right test pad on the camera PCB and connect a wire from this pad to the header pin as shown.

	![Solder Wire](images/assembly4.jpg)

* Connect 0.1\" header wire and use hot glue too prevent becoming loose.	
	![Connect Header](images/assembly5.jpg)

* Unscrew the 2 screws on the back of the camera, and screw on the supplied CS Lens Seat, put some Loctite on the screws (not excessive) and do not overtighten.  Cap the CS Lens Seat to protect the sensor.

	![CS Lens Seat Installed](images/assembly8.jpg)
	
* Install Flat-Flex Cable, contacts should be orientated toward the PCB.

	![Flat-Flex Bottom](images/assembly10.jpg)
	
## OTEStamper Board

* Place the 3D-Printed Lozenge on the long slot in the PCB (to provide support for the GPS board) and using the 5-pin yellow header supplied with the GPS, solder the GPS board to the OTEStamper board.  Clip the excess header.
	
	![GPS Board Soldered](images/assembly20.jpg)
	
* Using the 2.6mm spacer, 2.5mm x 8mm bolt, and 2.5mm Nut, the GPS board through the mounting hole to the OTEStamper Board.

	![GPS Mounting Hole](images/assembly21.jpg)

* Hot-Glue the 3D-Printed Power Socket Block underneath the OTEStamper Board.

	![3D-Printer Power Socket Block](images/assembly22.jpg)
	
* Attach GPS Pigtail, being careful to push the connector on squarely to avoid damage.  Zip-tie the cable as shown to avoid accidental disconnection.  Trim the free end of the zip-tie.

	![GPS Pig-Tail Attached](images/assembly23.jpg)
	
* Attach Hex Standoff and bolts as shown.

	![Hex Standoffs Attached](images/assembly24.jpg)
	
* Clip the 0V pin on the 0.1\" right angled header.

	![Hex Standoffs Attached](images/assembly25.jpg)
	
## Case Preparation

* Super-Glue the 4 Camera Mounting Posts to the case bottom in the indents provided.  Ensure the indents are cleared out sufficiently so that the posts will sit flush within the groove, as clearance has been designed to be a minimum for the camera board.

	![Super-Glued Mounting Posts](images/assembly30.jpg)
	
* Insert the 4 2.5mm nuts in the recesses in the case bottom.  Use a drop of super-glue at the edge of the nut to glue to the case such that the glue wicks into the space.  Do not foul the inside thread with super-glue.

	![Super-Glued Mounting Posts](images/assembly31.jpg)
	
* Cover the nuts with a layer of electrical tape to prevent any possibility of short-circuiting with the Raspberry Pi board.

	![Nuts Covered](images/assembly32.jpg)
	
* Attach the fan to the case, note the fan is oriented such that the label is towards the top of the case. The fan clips are very delicate and can snap, snap in place carefully, and do not force.  If a clip breaks, super-glue can be used to fix.

 	![Fan and Pigtail attached](images/assembly41.jpg)