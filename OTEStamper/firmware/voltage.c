#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include "voltage.h"


volatile uint16_t voltage = 10;



void voltageInit(void)
{
	ADMUX	= 0b01000010;			// 3.3V Ref, Set channel to ADC2
	ADCSRA	= _BV(ADEN) | _BV(ADIE) | 0x07;	// Enable ADC, Enable Interrupt, Set Prescaler=128
	voltageStartRead();
}


void voltageStartRead(void)
{
	ADCSRA |= _BV(ADSC);
}



ISR(ADC_vect)
{
	voltage = ADCL;
	voltage |= ADCH << 8;
}
