#include "config.h"

#include <avr/io.h>
#include "debug.h"
#include "fan.h"



void fanInit(void)
{
	PIN_FAN_DDR |= PIN_FAN_BIT;     // Set FAN pin to output
	fanEnable();
}



// Enable the fan

void fanEnable(void)
{
	PIN_FAN_PORT |= PIN_FAN_BIT;
}



// Disable the fan

void fanDisable(void)
{
	PIN_FAN_PORT &= ~PIN_FAN_BIT;
}
