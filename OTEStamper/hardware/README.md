## Version 0.9b
	
* Initial

## Version 0.9c

* No electrical changes.
* Moved label for D1 below diode and clarified orientation for the Buck Regulator to make it less likely to assemble wrong way round.

## Version 1.0.0
	
* Added HOT label around buck convertor and back protection FET
* Removed 4 pin flat flex to camera board
* Moved JP2 right to allow clearance of U2
* Moved buzzer to bottom of the board and rotated 45 to make room for 150uF capacitor
* Added 150uF capacitor to limit surge current to regulator
* Moved Fan header so header pins easily clear GPS
* Added JST 2 Pin Connector For Different 12V Source
* Changed Q1/Q2 to MMBT2222A-TP for increased fan current upto 500mA

## Version 1.0.0 (no board revision)

Extended monostable duration from 1.2us to 1ms to account for
different versions of the camera module with varying XVS pulse lengths, which
can cause multiple pulses for each XVS signal:

 * Changed R18 from 1K to 10K
 * Changes C12 from 1nF to 0.1uF


## Future Ideas

1. Maybe look at switching out back protection FET to one with lower RDS as the voltage drop across is large at high currents (buck can keep up fine).


## PSU Characterisation

1. Voltage range is 7.5 - 18V, specified range to the user is 12V-15V @ 4A

2. Voltage dropout occurs at 7.5V

3. Buck starts to current limit (switch the PSU on and off) at 4.1A

4. Max temperature ofr the bucks convert (4A @ 18V) is 130C

5. Damage to the buck convertor will occur at 20V

6. Fuse never gets triggered during normal use.  Would only get trigger if there was failure on the board itself.


| PSU Output | Supply Input | Temperature |
| ---------- | ------------ | ----------- |
| 0.2A @ 5.04V | 0.062A @ 18V | Room |
| 1A @ 5.02V | 0.304A @ 18V | 42C |
| 2A @ 4.97V | 0.604A @ 18V | 57C |
| 3A @ 4.89V | 0.920A @ 18V | 85C |
| 4A @ 4.79V | 1.243A @ 18V | 125C |

## Testing

1. Power at 12V at current limit 40mA, power usage should be approx 25-30mA, GPS LED should be on
2. Test voltage TP1 = Just above 5V
3. Test voltage TP2 = 5V
4. Test in Software with Raspberry Pi and Camera Connected:

	a) Install firmware
	
		make reset
		make writefuses
		make install

	b) GPS
	
	c) PPS
	
	d) Test Buzzer and Fan:
	
		cd ~/astrid/OTEStamper/test
		./spitest.py
	
	e) Record video and check all status buttons are green and video is recorded
	