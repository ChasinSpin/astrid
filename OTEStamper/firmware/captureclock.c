#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include <time.h>
#include <stdio.h>
#include "debug.h"
#include "eeprom.h"
#include "captureclock.h"
#include "spi.h"
#include "led.h"
#include "frameinterrupt.h"

// IMPORTANT: It takes about 5 seconds after firmware upload or restart for the GPS to be connected to and last_pps_duration to be valid
// (provided there's a GPS PPS Signal)

// Note: If a new leap second is added and the device is on when this happens, behaviour maybe undefined, switch off and restart to pick up the new second.


// This sets up 2 input capture timers that run exactly in sync at 8MHz (F_CPU) so it forms 1 timebase:
//
//	1. PPS on Timer 3
//	2. XVS on Timer 4
//
// Timer 3 has it's input capture register (ICR3) set and an interrupt generated everytime a PPS pulse occurs (rising edge, start of pulse)
// Timer 4 has it's input capture register (ICR4) set and an interrupt generated everytime a XVS pulse occurs (rising edge, start of pulse)
//
// The timers are 16 bit, so at 8Mhz, the timers overflow many times per second, so the Timer overflows for these timers are also monitored,
// however Timer 4 overflow is not monitored as it just mimics Timer 3, so is a waste of cycles.  Ordinarily a prescaler would be used
// in these situations, but that limits the resolution of timing, so was decided against.
//
// Because there are cpu execution times associated with any timer reset, this design does not do that, and allows the timer
// to continuously run, wrapping round at overflow.
//
// Timer 3 and 4 are in sync by stopping the timers during initialization. This was verified by inputting
// PPS into ICP4 too.
//
// 2 PPS pulses are required for timing information to be accurate
// if PPS pulses are lost or seem to be widely inaccurate, then timing information may also be compromised
//
// There are 2 times:
//	1. GPS time (what the GPS thinks the time is, which maybe different from the actual UTC time)
//	   GPS time is only used in the the GPS Module, time within this module is always UTC time
//	2. UTC/System Time (this is the system time)
//	   It's always attempted for this to be accurate, and capture_clock_status flags indicate when it may not be.
// Any difference between GPS Time and UTC time is due to the Leap Seconds from the GPS receiver not being determined.


//#define DEBUG_FRAME_TIMESTAMPS


#define MAX_TIMER_OVERFLOWS	183						// The number of timer overflows until a PPS signal is deemed lost (183 = ~1.5s)

static volatile uint8_t		timer_overflows = 0;				// Incremented everytime the timer overflows, and reset when a PPS pulse occurs
static volatile uint32_t	last_pps_duration = F_CPU;			// Duration between the last 2 PPS pulses in units of 1/F_CPU
static uint16_t			pps_offset = 0;					// How many cycles to the next timer overflow
volatile uint8_t		capture_clock_status = CC_STATUS_UNKNOWN;	// Returns the status flags of this module
static uint8_t			pps_acquisition_counter = 0;			// 0 = no recent pps pulses, 1 = 1 recent pps pulse, 2 = 2 recent pps pulses.  Is reset to zero if no pulse is received after 1.5s
static uint8_t			frame_sequence = 0;				// The sequence number of the frame, incremented on each new frame

#define LEAP_SECONDS_SOFTWARE_DEFAULT 18	// Update after a leap second has been added (infrequent)
	
int8_t			leapSeconds;
static uint8_t		eepromLeapSeconds;
volatile time_t		systemtime_secs = 0;

static uint8_t		test_timing = 0;

volatile uint8_t frameInterruptEnabled = 0;

struct frameInfoQueueEntry frameInfoQueue[FRAME_INFO_QUEUE_MAX];
volatile uint8_t frame_info_queue_read_index = 0;
uint8_t frame_info_queue_write_index = 0;
volatile uint8_t frame_info_queue_size;



void captureclockInit(void)
{
        // Read the leap seconds from the eeprom
        eepromLeapSeconds = eepromReadLeapSeconds();

	if ( eepromLeapSeconds == 0xFF )	leapSeconds = (int8_t)LEAP_SECONDS_SOFTWARE_DEFAULT;
	else					leapSeconds = (int8_t)eepromLeapSeconds;

	// Setup Timer 3 and Timer 4 to set Input Capture Register with the time when the Input Capture Pin is triggered (no prescaler)
	TCCR3A	= 0;
	TCCR3B	= _BV(ICES3) | _BV(CS30);

	TCCR4A	= 0;
	TCCR4B	= _BV(ICES4) | _BV(CS40);

	GTCCR	|= _BV(TSM) | _BV(PSRSYNC);	// Stop all timers and reset prescaler, so we can reset timer 3/4 and they remain in sync

	TCNT3	= 0;				// Reset counter timer 3
	TCNT4	= 0;				// Reset counter timer 4

	TIMSK3	= _BV(ICIE3) | _BV(TOIE3);	// Setup the interrupt
	TIFR3 	= 0;				// Clear any pending interrupts

	TIMSK4	= _BV(ICIE4);			// Setup the interrupt
	TIFR4 	= 0;				// Clear any pending interrupts

	GTCCR	&= ~(_BV(TSM) | _BV(PSRSYNC));	// Start the timers
}



uint8_t captureclockStatus(void)
{
	return capture_clock_status;
}



void testTimingEnable(uint8_t enable)
{
	test_timing = enable;
	if ( ! test_timing )	ledDisable();
}


void setFrameInterruptEnabled(uint8_t enabled)
{
	cli();
	frame_sequence = 0;
	frame_info_queue_read_index = 0;
	frame_info_queue_write_index = 0;
	frame_info_queue_size = 0;
	frameInterruptEnabled = enabled;
	sei();
}


void captureclockUpdateWithGPS(time_t gpsTime, int8_t gpsLeapSeconds, uint8_t gpsLeapSecondsFirmwareDefault)
{
	capture_clock_status &= ~CC_STATUS_LEAP_SECONDS_SOURCE_MSK;

	// Determine the leap seconds
	if  ( gpsLeapSecondsFirmwareDefault )
	{
		// We are unusure of the number of leap seconds as they are coming from the firmware default
		if ( eepromLeapSeconds == 0xFF )
		{
			// We have nothing in eeprom (it's the erased default), set to the software default
			capture_clock_status	|=  CC_STATUS_LEAP_SECONDS_SOURCE_SOFTWARE;
			leapSeconds		 = (int8_t)LEAP_SECONDS_SOFTWARE_DEFAULT;
		}
		else
		{
			// Use what we have in eeprom
			capture_clock_status	|= CC_STATUS_LEAP_SECONDS_SOURCE_EEPROM;
			leapSeconds	 	= (int8_t)eepromLeapSeconds;
		}

		cli();
		systemtime_secs = gpsTime - (leapSeconds - gpsLeapSeconds);
		sei();
	}
	else
	{
		capture_clock_status |= CC_STATUS_LEAP_SECONDS_SOURCE_GPS;

		// If the eeprom leap seconds differs from the GPS, then store in eeprom (have to disable interrupts during this)
		if ( eepromLeapSeconds != gpsLeapSeconds )
		{
			eepromLeapSeconds = gpsLeapSeconds;
			cli();
			eepromUpdateLeapSeconds(eepromLeapSeconds);
			sei();

		}

		cli();
		if ( systemtime_secs != gpsTime )
		{
			systemtime_secs = gpsTime;	
		}
		sei();

		if ( gpsLeapSeconds != leapSeconds )	capture_clock_status |= CC_STATUS_TIME_JUMPED;

		leapSeconds = gpsLeapSeconds;
	}
}



// PPS Interrupt

ISR(TIMER3_CAPT_vect)
{
        // We've had a PPS pulse, read ICR3 to get the counter time this occured
        uint16_t counter                  = ICR3;

	systemtime_secs ++;

	if ((TIFR3 & _BV(TOV3)) && (counter < 20000))
	{
		TIFR3 &= _BV(TOV3);
		timer_overflows ++;
	}

	// Take the number of overflows (-1 because the first overflow includes pps_offset and counter already)
	// and shift those to be the upper 2 bytes of the uin32_t, then add on counter
	// finally add on the ICR3 value we store at the beginning of the previous pps (pps_offset)
        last_pps_duration       = ((uint32_t)(timer_overflows - 1) << (uint32_t)16) | (uint32_t)counter;
	last_pps_duration	+= pps_offset;

	timer_overflows	= 0;

	if ( test_timing )
	{
		if ((systemtime_secs % 10) == 0)
			ledDisable();
		else	ledEnable();
	}

	// Setup for the next pulse
	pps_offset		= ~counter;	// Figure out how many cycles to the next overflow, this is equivalent to 65535-counter, but is faster

	if ( pps_acquisition_counter < 2 )
	{
		pps_acquisition_counter ++;
		{
			if (pps_acquisition_counter == 2)
			{
				capture_clock_status |= CC_STATUS_PPS_SEEN | CC_STATUS_PPS_RECENT;
			}
		}
	}
}




// XVS Interrupt

ISR(TIMER4_CAPT_vect)
{
	#ifdef DEBUG_FRAME_TIMESTAMPS
		uint8_t t = 0x00;
	#endif

        // We've had an XVS pulse, read ICR4 to get the counter time this occurred
	uint16_t counter		= ICR4;

	uint8_t xvs_timer_overflows	= timer_overflows;
	time_t unixEpoch		= systemtime_secs;

	// If we've just crossed a potential overflow, we need to figure out if it's included in timer_overflows or not
	if (TCNT4 < counter)
	{
		// If we have an overflow flag set, it's not included
		if ( ! (TIFR3 & _BV(TOV3)) )
		{
			xvs_timer_overflows --;
			#ifdef DEBUG_FRAME_TIMESTAMPS
				t |= 0x01;
			#endif
		}
	}
	else
	{
		if (TIFR3 & _BV(TOV3))
		{
			TIFR3 &= _BV(TOV3);
			timer_overflows ++;
		//	xvs_timer_overflows ++;
			#ifdef DEBUG_FRAME_TIMESTAMPS
				t |= 0x02;
			#endif
		}
	}

	// Take the number of overflows (-1 because the first overflow includes pps_offset and counter already)
	// and shift those to be the upper 2 bytes of the uin32_t, then add on counter

	// Take the number of overflows (-1 because the first overflow includes pps_offset and counter already)
	// and shift those to be the upper 2 bytes of the uin32_t, then add on counter
	// finally add on the ICR4 value we store at the beginning of the previous pps (pps_offset).
	// There can also be the occurence when xvs_timer_overflows = 0, and the calculation wraps by 32bit
	// so we test for that too.
        uint32_t xvs_ticks_since_last_pps;
	if ( xvs_timer_overflows == 0 )
	{
		// No timer overflows to consider:
		// ~pps_offset is a equivalent to 65535-pps_offset
		#ifdef DEBUG_FRAME_TIMESTAMPS
			t |= 0x04;
		#endif
		uint16_t pps_offset_counter = ~pps_offset;
		if ( counter < pps_offset_counter )
		{
			// The ICR4 happened before the second change, so belongs to the last second
			// Subtract one overflow and one second
			xvs_ticks_since_last_pps = last_pps_duration - (uint32_t)(pps_offset_counter - counter);
			unixEpoch --;
			#ifdef DEBUG_FRAME_TIMESTAMPS
				t |= 0x20;
			#endif
		}	
		else
		{
			xvs_ticks_since_last_pps = (uint32_t)counter - (uint32_t)pps_offset_counter;
			#ifdef DEBUG_FRAME_TIMESTAMPS
				t |= 0x40;
			#endif
		}
	}
	else
	{
		#ifdef DEBUG_FRAME_TIMESTAMPS
			t |= 0x08;
		#endif
        	xvs_ticks_since_last_pps = ((uint32_t)(xvs_timer_overflows - 1) << (uint32_t)16) | (uint32_t)counter;
		xvs_ticks_since_last_pps += pps_offset;
	}

	if ( frameInterruptEnabled )
	{
		struct frameInfoQueueEntry *entry = &frameInfoQueue[frame_info_queue_write_index];
		// Queue size is assigned at read time
		entry->leapSeconds			= leapSeconds;
		#ifdef DEBUG_FRAME_TIMESTAMPS
			entry->clockStatus		= t;
		#else
			entry->clockStatus		= capture_clock_status;
		#endif
		entry->frame_sequence			= frame_sequence;
		entry->last_pps_duration		= last_pps_duration;
		entry->frame_ticks_since_last_pps	= xvs_ticks_since_last_pps;
		entry->frame_unix_epoch			= unixEpoch;

		frame_info_queue_size ++;
		frame_info_queue_write_index ++;
		frame_info_queue_write_index %= FRAME_INFO_QUEUE_MAX;
		frame_sequence ++;
	}

	if ( frameInterruptEnabled ) frameInterrupt();	// Generate the frame interrupt to say the frame time is ready to be read
}



// Timer overflow interrupt

ISR(TIMER3_OVF_vect)
{
	timer_overflows ++;
		
	// If we haven't had a pps pulse within the last 1.5 seconds, then update status to indicate no recent pps pulse
	if ( timer_overflows >= MAX_TIMER_OVERFLOWS )
	{
		capture_clock_status &= ~CC_STATUS_PPS_RECENT;
		pps_acquisition_counter = 0;
	}
}
