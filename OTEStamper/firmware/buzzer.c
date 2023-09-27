#include "config.h"

#include <avr/io.h>
#include "debug.h"
#include "buzzer.h"


#define BUZZER_FREQ		4000				// 4 KHz
#define CLK_CYCLES_FOR_BUZZER	((((F_CPU/8)/4000)/2) - 1)


// 4KHz Buzzer on Timer 0 and OC0A
// Although timer is running after calling this, buzzerEnable must be called to produce output

void buzzerInit(void)
{
	PRR0 &= ~_BV(PRTIM0);	// See data sheet - enable Timer/Counter0 module, not necessary, but datasheet mentions it, so just in case

	TCCR0A 	= _BV(WGM01); 	// Toggle OC0A on compare match and CTC Mode (not we enable 0C0A later)
	TCCR0B 	= _BV(CS01);  	// Set to 1MHz Prescaler

	OCR0A	= CLK_CYCLES_FOR_BUZZER;

	TCNT0	= 0;		// Reset counter

	PIN_BUZZER_DDR |= PIN_BUZZER_BIT;

	buzzerDisable();
}



// Enable the buzzer

void buzzerEnable(void)
{
	TCCR0A 	|= _BV(COM0A0);
}



// Disable the buzzer

void buzzerDisable(void)
{
	TCCR0A 	&= ~_BV(COM0A0);
	PIN_BUZZER_PORT &= ~PIN_BUZZER_BIT;
}
