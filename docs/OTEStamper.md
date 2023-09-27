# OTEStamper

## Introduction

[OTEStamper](https://github.com/ChasinSpin/OTEStamper) is hardware and firmware to provide a highly accurate GPS-based timing source for [Astrid](../README.md) to record astronomical Occultations, Transits, and Eclipses (OTE) on a Raspberry Pi as a video file.  Using the [OTEStamper](https://github.com/ChasinSpin/OTEStamper), these events are timestamped accurately so that they can be used for scientific purposes using commonly available Raspberry Pi hardware when paired with a telescope or zoom lens.  It can be used with the Raspberry Pi HQ or Global Shutter cameras currently.

Accurate timing with [OTEStamper](https://github.com/ChasinSpin/OTEStamper) is provided by using a GPS receiver with PPS capability ([GT-U7](https://www.amazon.com/Navigation-Satellite-Compatible-Microcontroller-Geekstory/dp/B07PRGBLX7/ref=sr_1_2?crid=ZLVK5XJ3YEOT&keywords=GT-U7&qid=1680044165&sprefix=gt-u7%2Caps%2C120&sr=8-2)) to update the clock on the Raspberry Pi to within 1uS accuracy and concurrently updates time in a microcontroller.  The board contains a real-time ATmega328pb microcontroller to monitor the 1PPS signal and flash an LED which is inserted into the light path of the sensor.  This LED is precisely controlled to flash at custom intervals and duration to determine exact timing within the video for both rolling and global shutters and quantify any delay. Overall accuracy better than 1.25uS is provided for frame timing.

## Accuracy and Delays

* GPS: Average of 2.35ns over 6 hours, with a sampling deviation of 6.7ns
* Delay from XVS Trigger (Camera) to MCU External Interrupt input seeing voltage high: 40.3ns
* Firmware timing accuracy over 5mins: Min-Max 1.25uS, Standard Dev: 0.26uS


## Programming

The ATmega328pb can be programmed directly from the Raspberry Pi, no additional hardware is required.

To view debugging serial print's from the firmware, uncomment DEBUG in config.h and ensure /boot/config.txt contains:
 
	[pi4]
	# Run as fast as firmware / board allows
	arm_boost=1
	
	dtoverlay=uart5

## Schematic/Board
[Schematic - PDF](hardware/OTEStamper.pdf)

[Eagle files](hardware)

## BOM (Bill Of Materials) - NEEDS UPDATING - USE Numbers BOM instead

| Quantity | Part | Value | Tolerance | Package | Description | Manufacturer | Supplier | Supplier Part # |
| -------- | ---- | ----- | --------- | ------- | ----------- | ------------ | -------- | --------------- |
|1|R11|68|5%|0603|Resistor|-|Digi-Key|-|
|13|R1,R2,R3,R4,R5,R6, R7,R8,R9,R10,R12, R13,R15|1K|5%|0603|Resistor|-|Digi-Key|-|
|1|R14|10K|5%|0603|Resistor|-|Digi-Key|-|
|2|C1,C2|12pF|20% C0G Min 10V|0603|Capacitor|-|Digi-Key|-|
|1|C5|1nF|20% X5R/7 Min 10V|0603|Capacitor|-|Digi-Key|-|
|3|C3,C4,C6|0.1uF Min 10V|20% X5R/7|0603|Capacitor|-|Digi-Key|-|
|1|Q1|MMBT3904LT1G|-|SOT23-BEC|General Purpose NPN Transistor|Onsemi|Digi-Key|MMBT3904LT1GOSCT-ND|
|1|U1|SN74AUP1T57DBV|-|SOT23-6|Single Supply Level Translator|Texas Instrument|Digi-Key|296-17524-1-ND|
|1|U2|ATMEGA328PB-AN|-|32-TQFP|ATmega328pb Microcontroller|Microchip Technology|Digi-Key|ATMEGA328PB-AN-ND|
|1|U3|SN74LVC1G123DCT|-|SSOP-8|Monostable|Texas Instruments|Digi-Key|296-18758-1-ND‎|
|1|XC1|RH100-8.000-10-1010-EXT-TR|-|4-SMD 3.2 x 2.5 x 0.8mm 4 pin|8 Mhz Crystal 10ppm 10pF Load|Raltron Electronics|Digi-Key|2151-RH100-8.000-10-1010-EXT-TRCT-ND|
|1|MODULE1|GT-U7|-|Module|NEO-6M Based GPS Module with PPS|Goouuu Tech|Amazon|[GT-U7 GPS board](https://www.amazon.com/Navigation-Satellite-Compatible-Microcontroller-Geekstory/dp/B07PRGBLX7/ref=sr_1_2?crid=ZLVK5XJ3YEOT&keywords=GT-U7&qid=1680044165&sprefix=gt-u7%2Caps%2C120&sr=8-2)||
|1|JP3|PRPC001SBAN-M71RC|-|0.1" Header|0.1" Right Angled Male Header 1x1|Sullins Connector Solutions|Digi-Key|S1111EC-01-ND|
|2|JP5,JP6|PRPC002SBAN-M71RC|-|0.1" Header|0.1" Right Angled Male Header 1x2|Sullins Connector Solutions|Digi-Key|S1111EC-02-ND‎|
|DNP|JP2|PRPC001SBAN-M71RC|-|0.1" Header|0.1" Right Angled Male Header 1x1|Sullins Connector Solutions|Digi-Key|S1111EC-01-ND|
|DNP|JP9,JP10|PRPC001SFAN-RC|-|0.1" Header|0.1" Male Header 1x1|Sullins Connector Solutions|Digi-Key|S1211EC-01-ND‎|
|1|X1|Adafruit 2222|-|0.1" Header|0.1" Female Header 2x20|[Adafruit](http://adafru.it/2222)|Digi-Key|1528-1785-ND|
|1|SP1|PS1240P02BT|-|PS12 12.2mm Dia|3V Piezo Buzzer Transducer (no internal oscillator)|TDK|Digi-Key|445-2525-1-ND|
|0.1|-|Adafruit 1950 or 1 x SparkFun PRT-10367|-|0.1" Header|Female/Female Jumper Leads 6", to hookup LED|Adafruit|Digi-Key|1528-1961-ND‎|
|1|-|HLMP-Y502-F0000|-|3mm T1 |Clear Green LED 40mcd, 2.0 Forward Voltage, 573nm, 55deg|Broadcom|Digi-Key|516-3248-ND|
|4|-|24332|-|-|24332 Hex Standoff M2.5 x 0.45 Alumnimum 12mm|Keystone Electronics|Digi-Key|36-24332-ND|
|12|****||-|-|Countersunk M2.5 x 0.45 x 14mm||||
|12|-|4707|-|-|Hex Nut 0.197" Steel M2.5 x 0.45|Keystone Electronics|Digi-Key|36-4707-ND|
|1|*** PCB||-||PCB|OSHPark|OSHPark|[OSHPark](http://www.oshpark.com/)|
|1|Fan|3368|-|30x30x8mm|5VDC 30x30x7.7mm Fan for Cooling|Adafruit or CanaKit Raspberry Pi Fan|Digi-Key|1528-1904-ND|
|1|*** Stencil|-|-|-|(Optional) |OSHStencil|OSHStencil|[OSHStencil](http://www.oshstencil.com/)| 
|1|*** Enclosure|-|-|-|3D Printed Enclosure|3D Printer|3D Printer||
|1|-||-|-|FFC 20cm 15 Pin Flexible Flat Cable for Raspberry Pi Module Camera||||

Notes: DNP = Do Not Populate, SMD sizes are imperial

## Adaptors
* C/CS to 1.25 adapter
* C/CS to 48mm dapater

## Next Design Revision

Nothing

## Future Wish List
* Lipo Battery (not sure about this one)
* Adafruit sell an 18650 3 cell 10Ah battery pack
* Maybe Peltier support



## ATmega328PB Programming

Read Fuses:

	raspi-gpio set 22 op
	raspi-gpio set 22 dl	# Reset - put in programming mode
	sudo avrdude -p m328pb -P /dev/spidev0.0 -c linuxspi -b 10000
	raspi-gpio set 22 dh
	
Makefile:

	(NEEDS UPDATING FOR 328pb)
	MCU=atmega328p
	AVRDUDEMCU=m328p
	FUSES=-U lfuse:w:0xFF:m -U hfuse:w:0xDA:m -U efuse:w:0x06:m
	#FUSES=-U lfuse:w:0x62:m -U hfuse:w:0xD9:m -U efuse:w:0x07:m    # DEFAULT ATmega328p shipping fuses
	CC=/usr/bin/avr-gcc
	CFLAGS=-g -Os -Wall -mcall-prologues -mmcu=$(MCU)
	OBJ2HEX=/usr/bin/avr-objcopy
	AVRDUDE=/usr/local/bin/avrdude
	TARGET=blinky
	
	all:
		$(CC) $(CFLAGS) $(TARGET).c -o $(TARGET)
		$(OBJ2HEX) -R .eeprom -O ihex $(TARGET) $(TARGET).hex
		rm -f $(TARGET)
	
	install: all
		raspi-gpio set 22 op
		raspi-gpio set 22 dl	# Reset - put in programming mode
		sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000 -U flash:w:$(TARGET).hex
		raspi-gpio set 22 dh
	
	noreset: all
		sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000 -U flash:w:$(TARGET).hex

	readfuses:
		raspi-gpio set 22 op
		raspi-gpio set 22 dl
		sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000		raspi-gpio set 22 dh
	
	writefuses:
		raspi-gpio set 22 op
		raspi-gpio set 22 dl
		sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000 $(FUSES)		raspi-gpio set 22 dh
	
	clean :
		rm -f *.hex *.obj *.o	
		
Blinky:

	#define F_CPU 8000000L	#include <avr/io.h>	#include <util/delay.h>	int main (void)	{   	     DDRD |= (1 << PD5);   	     for (;;)   	     {   	             PORTD ^= (1 << PD5);   	             _delay_ms(500);   	     }   	     return 0;	}

## OTEStamper SPI Protocol

The command protocol uses an SPI bus with a master (the Raspberry Pi) and a slave (the ATmega328pb).

The Atmega328p does not have double buffering when sending data as a slave, therefore either polling has to be implemented to minimize delay
or interrupts are used which take longer and require slower SPI transmission rates as SPDR can't be loaded with a new value until the last value has transmitted.  To solve this:

Transactions are completed as a one-byte concurrent read/write, i.e. CS is taken low, one byte is sent by the master at the same time
the slave is sending a byte.  Conceptually the slave doesn't respond to a command from the master until the next command is sent by the master.
Data is therefore preemptively preloaded by the slave based on what the slave thinks the master will need for the next command and the delay to
allow userspace processing happens during the idle period between spi transmissions.  This approach differs from conventional SPI register-based access.

Implemented on top of this level are higher-level transactions that are aware of this 1-byte delay:

| Device      | SPI Transaction | SPI Transaction | SPI Transaction | SPI Transaction| SPI Transaction |
| ----------- | --- | ------ | ---- | ---- | --- |
| Master TX:  | Cmd | 0xFF   | 0xFF | 0xFF | 0x00 |
| Slave TX:   | XX  | Data 1 | Data .. | Data N | CRC |

**Note: CS goes low then high for each byte transmission**

The master expects a certain length response for a particular command.  Also, it can only send commands 1 byte in length and no
data.

Due to the received data from the master by the slave being Cmd, 0xFF or 0x00 and commands can not be 0x00 or 0xFF, it's
possible for the slave to know what stage in the transmission from the master it is and can reset
the higher level transaction state if master/slave become out of sync.

Any multibyte values (Unsigned Int 32 for example), are sent little-endian (LSB first),

### CRC Calculation

The CRC is calculated using \_crc8\_ccit\_update() with a 0x00 initial value using the calculation here:
[avr-libc CRC Computatations](https://www.nongnu.org/avr-libc/user-manual/group__util__crc.html) 

The CRC calculation is calculated from: Cmd, Data1, Data.., DataN and does not include the CRC bytes.

Because the CRC also includes the Cmd sent by the Master at the start, it serves to confirm that the command sent to the slave from the master was not corrupted.

### Commands

| Command | Type | Description | Response Length (bytes) | Response (Data bytes) |
| ------- | ---- | ----------- | --------------- | --------------------- |
| 0x60 | Get | Get Status | 0x01 | See "Get Status" below |
| 0x70 | Get | ID Magic Number | 0x04 | 0x1C 0x2A 0x03 0xFD |
| 0x71 | Get | Firmware Version | 0x02 | Unsigned Int 16 bit |
| 0x72 | Set | LED On | 0x00 | - |
| 0x73 | Set | LED Off | 0x00 | - |
| 0x74 | Set | FAN On | 0x00 | - |
| 0x75 | Set | FAN Off | 0x00 | - |
| 0x76 | Set | Timing Test On | 0x00 | - |
| 0x77 | Set | Timing Test Off | 0x00 | - |
| 0x78 | Set | Cold Restart GPS | 0x00 | - |
| 0x79 | Set | Frame Timing Info Interrupt On | 0x00 | - |
| 0x7A | Set | Frame Timing Info Interrupt Off | 0x00 | - | 
| 0x7B | Set | Buzzer On | 0x00 | - | 
| 0x7C | Set | Buzzer Off | 0x00 | - | 
| 0x90 | Get | GPS Info | 0x1A | See "GPS Info" below |
| 0x91 | Get | Frame Timing Info | 0x10 | See "Frame Timing Info" below |
| 0x92 | Set | Confirmed Frame Received | 0x00 | See "Frame Timing Info" below |
| 0x93 | Get | Test Frame For Validation | 0x10 | 16 values sequentially starting 0x55, 0x56 etc. |

Commands are stateless apart from 0x91/0x92, where a queue is being used to prevent
lost transmissions.  After data has been successfully received via an 0x91, a 0x92 should be issued to confirm reception and delete that item from the queue.  If an 0x91 fails the CRC, then another 0x91 can be issued to try again.  Sequence numbers should
always be checked in the frames to ensure they are sequential, if the same frame number is seen again, then it means the 0x92 was not received, 0x92 should be sent again and the frame silently dropped as a duplicate.

Slave: Commands are not CRC'd on transmission from the master, therefore it is possible for the slave
to receive a corrupt command.  However, the master will also receive an invalid CRC on the response due to the CRC including the command.  At this point, the master can request a Get Status command to see if there was any unintended change to the slave due to the transmission error.  The only exception to this is if the command is corrupted to 0x92 (confirmed frame received). In this unlikely scenario, expected frame sequence numbers will jump and can be detected by the master.

Master: Commands are actioned by the slave when the command byte is received. Therefore reception of a correct CRC is confirmation that the command has been executed, even if the last 0x00 from the master is not received by the slave.

#### Get Status

1 byte status containing bit flags indicating items that are on.

| Bit | Description |
| --- | ----------- |
| 0 | LED On |
| 1 | FAN On |
| 2 | Buzzer On |
| 3 | Timing Test On |
| 4 | Frame Timing Info Interrupt On |

#### Frame Timing Info Interrupt

When the "Frame Timing Info Interrupt" is switched on (Cmd = 0x79), the following happens:

1. Frame sequence number is reset to 0
2. The Frame Info Queue on the OTEStamper is cleared
3. New XVS triggers cause Frame Info to be stored in the Frame Info Queue
4. Interrupts are generated on each addition to the Frame Info Queue

When the "Frame Timing Info Interrupt" is switched off (Cmd = 0x7A), interrupts
are no longer generated.

#### GPS Info

| Offset | Length (bytes) | Description | Type | 
| ------ | -------------- | ----------- | ---- |
| 0x00 | 4      | Latitude in decimal degrees * 10000000 | Int 32bit |
| 0x04 | 4      | Longitude in decimal degrees * 10000000 | Int 32bit | 
| 0x08 | 4      | Altitude in decimal degrees * 10 | Int 32bit | 
| 0x0C | 1      | The number of satellites used in the fix | Unsigned Int 8bit | 
| 0x0D | 1      | Fix: 0 = No gps packets receiver yet, 1 = Fix not available, 2 = 2D Fix, 3 = 3D Fix | Unsigned Int 8bit | 
| 0x0E | 2      | Position dilution of precision * 100 | Unsigned Int 16bit | 
| 0x10 | 2      | Horizontal dilution of precision * 100 | Unsigned Int 16bit | 
| 0x12 | 2      | Vertical dilution of precision * 100 | Unsigned Int 16bit | 
| 0x14 | 4      | Unix Epoch | Unsigned Int 32bit |
| 0x18 | 1      | Leap Seconds | Int 8bit |
| 0x19 | 1      | Clock Status | See below |


#### Frame Timing Info

| Offset | Length (bytes) | Description | Type | 
| ------ | -------------- | ----------- | ---- |
| 0x00 | 1 | Remaining frame info's in queue. 0x01 = current entry (normal), 0x00 = empty queue, 0x02 = 2 items | Unsigned Int 8bit |
| 0x01 | 1 | Leap Seconds | Int 8bit |
| 0x02 | 1 | Clock Status      | See below |
| 0x03 | 1 | Frame sequence # | Unsigned Int 8bit |
| 0x04 | 4 | Last PPS Duration 1sec (ticks) | Unsigned Int 32bit |
| 0x08 | 4 | Frame ticks since last PPS | Unsigned Int 32bit |
| 0x0C | 4 | Frame Unix Epoch | Unsigned Int 32bit |

If the frame timing queue is empty, only 0x00 will be returned, and the rest of the data for that frame will be zero.


### Clock Status

| Bit | Value       | Notes                                       |
| --- | ----------  | ------------------------------------------- |
| 0   | PPS\_SEEN | Set if pulse has been seen since startup |
| 1   | PPS\_RECENT  | Set if we've had 2 pulses in the last 2 seconds |
| 2   | LEAP\_SECONDS\_SOURCE_GPS  | Leap seconds from the GPS (normal) |
| 3   | LEAP\_SECONDS\_SOURCE\_EEPROM  | Leap seconds from the eeprom (normal) |
| 4   | LEAP\_SECONDS\_SOURCE\_SOFTWARE  | Leap seconds from the software (maybe degraded) |
| 5   | TIME\_JUMPED  | The time jumped, this bit is cleared on read |


## Frame Trigger (XVS) Timing


Reference: [IMX 296 Full Datasheet](https://en.sunnywale.com/uploadfile/2023/0327/IMX296LQR-C_Fulldatasheet_Awin.pdf)

The XVS pulse is the vertical sync pulse and it is emitted once for every frame (active low), it is emitted towards the end of the exposure of the frame.  When the pulse occurs, the pulse is timestamped by the OTEStamper board using timely Input Capture Registers on the ATmega328pb.

### XVS Acquisition Delay OTEStamper

The delay between XVS being generated and recorded on OTEStamper is:

| Reason | Delay |
| ------ | ----- |
| Pulseshaping, conversion to 3.3V logic | 40.3ns |
| Input Capture Time Delay on ATmega328pb for XVS | 1/8Mhz = 125ns (quantization) |
| Input Capture Time Delay on ATmega328pb for GPS PPS | 1/8Mhz = 125ns (quantization) |

Taking 1/2 the Input Capture Time Delay for the GPS PPS as being an average = 62.5ns,this means that on average all our timestamps are 62.5ns late.  Additionally, the Input Capture for the XVS pulse also has an average of 62.5ns.

Combined, the XVS timestamp is reported later than it actually occurred by 40.3 + 62.5 + 62.25ns = 165.3ns and this value should be subtracted from the time reported by OTEStamper (this is not corrected for in OTEStamper due to processing time constraints.  Note that the input capture time delay variability (PPS and XVS) due to level change possibly not lining up with CPU clock frequency (quantization) creates 125ns x 2 = 250ns worse case timing error by OTEStamper.  So timing accuracy is +/- 250ns.

### Calculating Frame Start Time

[IMX 296 Full Datasheet](https://en.sunnywale.com/uploadfile/2023/0327/IMX296LQR-C_Fulldatasheet_Awin.pdf) *(Pulse Output Function - Image Drawing of Pulse Output Function in Global Shutter (Normal Mode))* denotes that "Normal Mode" for the IMX296 has XVS occurring towards the end of the exposure of the sensor.  The end of the exposure of the frame occurs 4 XHS pulses (the communication period) after the XVS pulse.

The XHS pulses (also called the 1H Period) is 14.81uS, there for the end time of the frame is XVS + 4 x 14.81uS = XVS + 59.24uS.

This means that to arrive at the start time of the frame, the exposure duration needs to be subtracted from XVS + 59.24uS.

### Putting It Together

Frame End Time = ((OTEStamper XVS Time - 165.3ns) + 59.24us) = OTEStamper XVS Time + 0.0000590747s

Frame Start Time = Frame End Time - Exposure Duration

Absolute Accuracy = 250ns + 2.35ns(GPS) + 6.7ns(GPS) = +/-259.02ns





