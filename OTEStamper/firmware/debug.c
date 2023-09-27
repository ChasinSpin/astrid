#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include "debug.h"
#include "circbuf.h"


// Uses Timer 1 running at 9600 baud, generating overflow interrupts
// to bit bang a pin (does not use delay)

#ifdef DEBUG


#define DEBUG_TX_BUF_LEN 254
static struct circbuf cb_debug_tx;
static uint8_t buf_debug_tx[DEBUG_TX_BUF_LEN];



#define BAUD			9600
#define CLK_CYCLES_FOR_BAUD	((F_CPU/BAUD)-1)



void debugInit(void)
{
	circbuf_create(&cb_debug_tx, buf_debug_tx, DEBUG_TX_BUF_LEN);

	// Setup the pin as output
	PIN_DEBUG_DDR	|= PIN_DEBUG_BIT;
	PIN_DEBUG_PORT	|= PIN_DEBUG_BIT;

	// Setup Timer 1 to generate an overflow interrupt at 9600 baud
	TCCR1A	= 0;				// Sets up Clear Timer On Compare (CTC mode) to OCR1A
	TCCR1B	= _BV(WGM12) | _BV(CS10);	// Sets up Clear Timer On Compare (CTC mode) to OCR1A, and No Clock Prescaler

	// These 16 bit registers need to be updated automatically, but during setup in otestamper.c, we already disable interrupts, so we're good
	OCR1A	= CLK_CYCLES_FOR_BAUD;
        TCNT1	= 0;            // Reset counter

	TIMSK1	= _BV(OCIE1A);	// Setup the interrupt
	TIFR1 	= 0;		// Clear any pending interrupts
}



void debugChar(unsigned char ch)
{
        if ( circbuf_put(&cb_debug_tx, ch) )
        {
		// Ordinarily we would print out a message here, but as we're using this buffer
		// to print out this message, we can't
        }
}



// Hex with 0x in front

void debugHexSub(uint8_t x)
{
	uint8_t ch;
	uint8_t ones = x/16;
	uint8_t tens = x%16;

	if ( ones >= 10 )	ch = 'A' + (ones - 10);
	else			ch = '0' + ones;
	debugChar(ch);

	if ( tens >= 10 )	ch = 'A' + (tens - 10);
	else			ch = '0' + tens;
	debugChar(ch);
}



// Hex with 0x in front

void debugHex(uint8_t x)
{
	debugChar('0');
	debugChar('x');

	debugHexSub(x);
}



void debugHex32(uint32_t x)
{
	debugChar('0');
	debugChar('x');
	
	debugHexSub( (uint8_t)((x >> 24) & 0xFF) );
	debugHexSub( (uint8_t)((x >> 16) & 0xFF) );
	debugHexSub( (uint8_t)((x >> 8) & 0xFF) );
	debugHexSub( (uint8_t)(x & 0xFF) );
}



// Prints out v as a decimal number, displays leading zeros is display_leading_zeros is set
// dp is where to place the decimal point, 0 if there's no decimal place

void debugDecU32(uint32_t v, uint8_t display_leading_zeros, uint8_t dp)
{
	uint32_t n;
	uint8_t display_zeros = display_leading_zeros;

	uint8_t i;
	uint32_t div;
	for (div = 1000000000, i = 10; div >= 1; div /= 10, i--)
	{
		if ( i == dp )	DEBUG_CHAR('.');

		n = v/div; v = v%div;
		if ( display_zeros || n > 0 )
		{
			DEBUG_CHAR(n + '0');
			display_zeros = 1;
		}
	}
}



// Prints out v as a decimal number, displays leading zeros is display_leading_zeros is set
// dp is where to place the decimal point, 0 if there's no decimal place

void debugDecS32(int32_t v, uint8_t display_leading_zeros, uint8_t dp)
{
	if ( v < 0 )
	{
		DEBUG_CHAR('-');
		v = -v;
	}
	debugDecU32((uint32_t)v, display_leading_zeros, dp);
}



void debugStr(char *str)
{
	unsigned char *p;

	p = (unsigned char *)str;
	while (*p)
	{
		debugChar(*p);
		p ++;
	}
}



// Send bit on timer 1 overflow

ISR(TIMER1_COMPA_vect)
{
        static uint8_t ch;
	static int8_t bit = -1;	// The bit that's currently being transmitted. -1 = Idle, 0 = Start, 1=Bit1(LSB), ... 8=Bit8(MSB), 9 = Stop

	if (bit == -1 || bit == 10)
	{	
                if ( circbuf_get(&cb_debug_tx, &ch) )
		{
			// If we have a character waiting, start to transmit it
			bit = 0;
		}
		else
		{
			// No character, so we idle
			bit = -1;
		}
	}

	if ( bit == 0 )
	{
		// Start bit
		PIN_DEBUG_PORT &= ~PIN_DEBUG_BIT;
	}
	else if (bit == 9 )
	{
		// Stop bit
		PIN_DEBUG_PORT |= PIN_DEBUG_BIT;
	}
	else
	{
		// Transmit bit and shift
		if ( ch & 0x01)	PIN_DEBUG_PORT |= PIN_DEBUG_BIT;
		else		PIN_DEBUG_PORT &= ~PIN_DEBUG_BIT;

		ch >>= 1;
	}

	bit ++;
}

#endif
