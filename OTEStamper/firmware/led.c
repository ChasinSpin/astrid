#include "config.h"

#include <avr/io.h>
#include "debug.h"
#include "led.h"



void ledInit(void)
{
	PIN_LED_DDR |= PIN_LED_BIT;     // Set LED pin to output
	ledDisable();
}



// Enable the led

void ledEnable(void)
{
	PIN_LED_PORT |= PIN_LED_BIT;
}



// Disable the led

void ledDisable(void)
{
	PIN_LED_PORT &= ~PIN_LED_BIT;
}



// Toggle the led

void ledToggle(void)
{
	PIN_LED_PORT ^= PIN_LED_BIT;
}
