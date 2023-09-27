#include "config.h"

#include <avr/io.h>
#include "frameinterrupt.h"



void frameInterruptInit(void)
{
	PIN_FRAME_INT_DDR |= PIN_FRAME_INT_BIT;     	// Set FRAME_INT pin to output
	PIN_FRAME_INT_PORT &= ~PIN_FRAME_INT_BIT;	// Switch off
}



// Generates a frame interrupt to the raspberry pi, informing it that the frame is ready
// Pulse length is about is about 4 cpu cycles (500ns)

void frameInterrupt(void)
{
	PIN_FRAME_INT_PORT |= PIN_FRAME_INT_BIT;	// Switch on
	PIN_FRAME_INT_PORT &= ~PIN_FRAME_INT_BIT;	// Switch off
}
