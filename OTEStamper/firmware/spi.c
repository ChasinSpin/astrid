#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>
#include <time.h>
#include <util/crc16.h>
#include "debug.h"
#include "captureclock.h"
#include "led.h"
#include "fan.h"
#include "buzzer.h"
#include "gps.h"
#include "spi.h"
#include "voltage.h"



static uint32_t otestamper_id = OTESTAMPER_ID;
static uint16_t firmware_version;

static uint8_t status = 0x02;

#define STATUS_FLAG_LED_BIT				0
#define STATUS_FLAG_FAN_BIT				1
#define STATUS_FLAG_BUZZER_BIT				2
#define STATUS_FLAG_TIMING_TEST_BIT			3
#define STATUS_FLAG_FRAME_TIMING_INFO_INTERRUPT_BIT	4



// Enables SPI in Mode 0 (CPOL=0, CPHA=0), MSB First, Slave, 2MHz is the theoretical maximum speed
// although the speed is always driven by the master.

void spiInit(uint16_t firmwareVersion)
{
	static uint8_t sink;

	firmware_version = firmwareVersion;

	// Make MOSI and SCK input pins
	PIN_SPI_CS_DDR		&= ~PIN_SPI_CS_BIT;		// Set CS to input
	PIN_SPI_SCLK_DDR	&= ~PIN_SPI_SCLK_BIT;		// Set SCLK to input
	PIN_SPI_MOSI_DDR	&= ~PIN_SPI_MOSI_BIT;		// Set MOSI to input
	PIN_SPI_MISO_DDR	|= PIN_SPI_MISO_BIT;		// Set MISO to output

	SPCR0			= _BV(SPE);			// Setup the SPI registers (Slave)

	// Clear any prior errors
	// Have to do this craziness to stop the compiler optimizing it away
	sink			= SPSR0;
	sink			= SPDR0;
	sink			= 0;
	SPDR0			= sink;

	SPCR0			|= _BV(SPIE);			//  Enable SPI Recived/Sent Interrupt (SPI transfer is complete)
}



static inline void handle_transaction(void)
{
	static uint8_t read_index, crc, tx, rx, *ptr, cmd = 0;

	// Read data the master sent us
	rx = SPDR0;

	if	( rx == 0xFF )	;		// During transmission
	else if ( rx == 0x00 )			// End of transmission
	{
		cmd		= 0x00;		// Prevent the cmd state machine being run
		SPDR0		= 0x00;		// Load it with something we don't care what
		return;
	}
	else			// Command
	{
		cmd		= rx;
		read_index	= 0;
		crc		= _crc8_ccitt_update(0x00, cmd);
	}

	// These are orderded in order of importance for speed reasons
	// A "loose" state machine to optimize performance
	// This is fully expanded out, so there's repition to avoid more cycles used by if/else

	switch(cmd)
	{
		case 0x91:	// Frame Timing Info
				if ( read_index == 0 )		{ ptr = (uint8_t *)&frameInfoQueue[frame_info_queue_read_index]; ptr[0] = frame_info_queue_size; }
				if ( read_index == 0x10 )	{ tx  = crc; cmd = 0x00; }
				else				tx  = *(ptr++);
				break;

		case 0x92:	// Confirmed Frame Received
				if ( read_index == 0 )
				{
					if ( frame_info_queue_size > 0 )
					{
                				frame_info_queue_size --;
                				frame_info_queue_read_index ++;
                				frame_info_queue_read_index %= FRAME_INFO_QUEUE_MAX;
					}
					tx = crc;
					cmd = 0x00;
				}				
				break;

		case 0x79:	// Frame Timing info interrupt On
				if ( read_index == 0 )
				{
					status |=_BV(STATUS_FLAG_FRAME_TIMING_INFO_INTERRUPT_BIT);
					setFrameInterruptEnabled(1);
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x7A:	// Frame Timing info interrupt Off
				if ( read_index == 0 )
				{
					status &= ~_BV(STATUS_FLAG_FRAME_TIMING_INFO_INTERRUPT_BIT);
					setFrameInterruptEnabled(0);
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x90:	// GPS Info
				if ( read_index == 0 )		ptr = (uint8_t *)&gpsdata_buffers[gpsdata_read_index];
				if ( read_index == 0x14 )	ptr = (uint8_t *)&systemtime_secs;
				if ( read_index == 0x18 )	ptr = (uint8_t *)&leapSeconds;
				if ( read_index == 0x19 )	ptr = (uint8_t *)&capture_clock_status;
				if ( read_index == 0x1A )	ptr = (uint8_t *)&voltage;
				if ( read_index == 0x1C )	{ tx  = crc; cmd = 0x00; }
				else				tx  = *(ptr++);
				break;

		case 0x60:	// Get Status
				if ( read_index == 0 )	tx = status;
				if ( read_index == 1 )	{ tx  = crc; cmd = 0x00; }
				break;

		case 0x72:	// LED On
				if ( read_index == 0 )
				{
					status |= _BV(STATUS_FLAG_LED_BIT);
					ledEnable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x73:	// LED Off
				if ( read_index == 0 )
				{
					status &= ~_BV(STATUS_FLAG_LED_BIT);
					ledDisable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x74:	// FAN On
				if ( read_index == 0 )
				{
					status |= _BV(STATUS_FLAG_FAN_BIT);
					fanEnable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x75:	// FAN Off
				if ( read_index == 0 )
				{
					status &= ~_BV(STATUS_FLAG_FAN_BIT);
					fanDisable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x76:	// Timing Test On
				if ( read_index == 0 )
				{
					status |= _BV(STATUS_FLAG_TIMING_TEST_BIT);
					testTimingEnable(1);
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x77:	// Timing Test Off
				if ( read_index == 0 )
				{
					status &= ~_BV(STATUS_FLAG_TIMING_TEST_BIT);
					testTimingEnable(0);
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x78:	// Cold Restart GPS
				if ( read_index == 0 )
				{
					gpsColdStartReset();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x7B:	// Buzzer On
				if ( read_index == 0 )
				{
					status |= _BV(STATUS_FLAG_BUZZER_BIT);
					buzzerEnable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x7C:	// Buzzer Off
				if ( read_index == 0 )
				{
					status &= ~_BV(STATUS_FLAG_BUZZER_BIT);
					buzzerDisable();
					tx = crc;
					cmd = 0x00;
				}
				break;

		case 0x70:	// ID Magic Number
				if ( read_index == 0 )	ptr = (uint8_t *)&otestamper_id;
				if ( read_index == 4 )	{ tx  = crc; cmd = 0x00; }
				else			tx  = *(ptr++);
				break;

		case 0x71:	// Get Firmware Version
				if ( read_index == 0 )	ptr = (uint8_t *)&firmware_version;
				if ( read_index == 2 )	{ tx  = crc; cmd = 0x00; }
				else			tx  = *(ptr++);
				break;

		case 0x93:	// Test Frame For Validation
				if ( read_index == 16 )	{ tx = crc; cmd = 0x00; }
				else			tx = 0x55 + read_index;
				break;

		case 0x00:	// No command
				tx = 0x00;
				break;

		default:
				break;
	}

	// Preload the byte we wish to transmit on the next transaction
	SPDR0 = tx;

	// Update crc
	crc = _crc8_ccitt_update(crc, tx);

	read_index ++;
}



// SPI transfer is complete (this is both receive and transmit as they both happen concurrently)

ISR(SPI0_STC_vect)
{
	static uint8_t rx, status, sink;

	handle_transaction();

	// Check for write collision, although it should never happen
	if ( SPSR0 & WCOL )
	{
		status	= SPSR0;
		rx	= SPDR0;
		sink	= status;
		sink	= rx;
		status	= sink;
	}
}
