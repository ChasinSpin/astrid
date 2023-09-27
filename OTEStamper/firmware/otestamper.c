#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <time.h>
#include "debug.h"
#include "spi.h"
#include "usart.h"
#include "buzzer.h"
#include "led.h"
#include "fan.h"
#include "captureclock.h"
#include "frameinterrupt.h"
#include "gps.h"
#include "eeprom.h"



// Timers:
//	Timer 0: 8-bit:  Buzzer @ 4KHz
//	Timer 1: 16-bit: 8MHz PPS Accurate Timer (this counts intervals very precisely)



// IMPORTANT: Why do some 16-bit timer registers sometimes get trashed? https://www.nongnu.org/avr-libc/user-manual/FAQ.html#faq_use_bv
// Check Volts on GPS TX are 0-3.3V on other receiver


int  main (void)
{
	cli();				// Global interrupts disabled whilst we setup

	// Initialize everything
#ifdef DEBUG
	DEBUG_INIT;			// Must be before spiInit as spi uses debug
#else
	frameInterruptInit();
#endif

	eepromInit();
	eepromUpdateVersion(FIRMWARE_VERSION);
	#ifdef DEBUG
		uint16_t version = eepromReadVersion();
	#endif

	ledInit();
	fanInit();
	spiInit(FIRMWARE_VERSION);
	usartInit();
	buzzerInit();
	gpsInit();
	captureclockInit();


	sei();				// Global interrupts enabled

	DEBUG_CHAR('\n');
	DEBUG_STR("Version:");
	DEBUG_HEX32((uint32_t)version);
	DEBUG_CHAR('\n');

        DEBUG_STR("EELeapSecs:");
        DEBUG_HEX(eepromReadLeapSeconds());
        DEBUG_CHAR('\n');

	//gpsColdStartReset();

	uint32_t count = 0;

	for (;;)
	{
		gpsProcess();

		/*
		if (( count % 10000 ) == 0)
		{
                	DEBUG_STR("Status: ");
                	DEBUG_HEX(captureclockStatus());
                	DEBUG_CHAR('\n');
		}
		*/

		count ++;
	}

	return 0;
}
