#include "config.h"

#include <avr/eeprom.h>
#include "debug.h"
#include "eeprom.h"


#define EEPROM_ADDR_VERSION 		0x00	// 2 bytes
#define EEPROM_ADDR_LEAP_SECONDS	0x02	// 1 byte


void eepromInit(void)
{
}



// Must be called with interrupts disabled

uint16_t eepromReadVersion(void)
{
	uint16_t ret;
	ret = eeprom_read_word((uint16_t *)EEPROM_ADDR_VERSION);
	return ret;
}



// Must be called with interrupts disabled

void eepromUpdateVersion(uint16_t v)
{
	eeprom_update_word((uint16_t *)EEPROM_ADDR_VERSION, v);
}



// Must be called with interrupts disabled

uint8_t eepromReadLeapSeconds(void)
{
	uint8_t ret;
	ret = eeprom_read_byte((uint8_t *)EEPROM_ADDR_LEAP_SECONDS);
	return ret;
}



// Must be called with interrupts disabled

void eepromUpdateLeapSeconds(uint8_t v)
{
	eeprom_update_byte((uint8_t *)EEPROM_ADDR_LEAP_SECONDS, v);
}
