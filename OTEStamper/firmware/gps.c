#include "config.h"

#include <avr/io.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "debug.h"
#include "usart.h"
#include "gps.h"
#include "captureclock.h"
#include "spi.h"


#define MAX_NMEA_MSG_SIZE 82

#define UBX_MSG_MAX 20
#define UBX_PAYLOAD_MAX 10



struct gpsdata gpsdata;
struct gpsdata gpsdata_buffers[GPSDATA_MAX_BUFFERS];
volatile uint8_t gpsdata_read_index = 0;
uint8_t gpsdata_write_index = 0;



void gpsInit(void)
{
	gpsdata.fix = 0;
}



// Sends a USB message

static void sendUBXMsg(uint8_t classId, uint8_t messageId, void *payload, uint8_t payloadLen)
{
	uint16_t bufLen = 0;
	uint8_t buf[UBX_MSG_MAX];

	if ( payloadLen > UBX_PAYLOAD_MAX)  {
		DEBUG_STR("sendUBXMsg: len too large.  Transmission aborted ");
		return;
	}

	// Setup the header
	buf[bufLen++] = 0xB5;
	buf[bufLen++] = 0x62;
	buf[bufLen++] = classId;
	buf[bufLen++] = messageId;
	buf[bufLen++] = payloadLen & 0xFF;
	buf[bufLen++] = payloadLen >> 8;

	// Copy the payload in
	for (uint8_t i = 0; i < payloadLen; i ++ )
	{
		((uint8_t *)(buf+bufLen))[i] = ((uint8_t *)payload)[i];
	}
	bufLen += payloadLen;

	// Calculate checksum
	uint8_t ck_a = 0, ck_b = 0;

	for ( uint16_t i = 2; i < bufLen; i ++ )
	{
		ck_a += buf[i];
		ck_b += ck_a;
	}

	buf[bufLen++] = ck_a;
	buf[bufLen++] = ck_b;

	usartPutData(buf, bufLen);
}



// Disables GPGSV, GPVTG, GPGLL, GPRMC as we don't need the information as it's duplicate, it's many lines and takes up a lot of CPU resources
// Enables PUBX,04 time message (which include leap seconds)

static void gpsMessageSetup(void)
{
	// Disable messages we don't need
	usartPutStr("$PUBX,40,GSV,0,0,0,0*59\r\n");
	usartPutStr("$PUBX,40,VTG,0,0,0,0*5E\r\n");
	usartPutStr("$PUBX,40,GLL,0,0,0,0*5C\r\n");

	// We need RMC for the raspberry pi to determine system time from GPS
	//usartPutStr("$PUBX,40,RMC,0,0,0,0*47\r\n");

	// Enable PUBX,04 time messages at 1 second intervals
	// Reference CFG-MSG Set Message Rate: https://content.u-blox.com/sites/default/files/products/documents/u-blox6-GPS-GLONASS-QZSS-V14_ReceiverDescrProtSpec_%28GPS.G6-SW-12013%29_Public.pdf
	uint8_t data[] = {0xF1, 0x04, 0x01};
	sendUBXMsg(0x06, 0x01, data, 3);
}



// Does a cold reset of the gps receiver for testing

void gpsColdStartReset(void)
{
	uint8_t payload[] = {0xFF, 0xFF, 0x00, 0x00};

	sendUBXMsg(0x06, 0x04, payload, 4);
}



// Like strcmp, but , or \0 mark the end of the match

static uint8_t zstrcmp(char *s1, uint8_t *s2)
{
	uint8_t *p1 = (uint8_t *)s1;

	for (; *p1 && *s2 && ( *p1 != ',' ) && ( *s2 != ','); p1++, s2++)
	{
		if ( *p1 != *s2 )	return 0;
	}

	return 1;
}



// Gets field "index" from "str" delimited by "delimiter" and puts it in "result"

static void getField(uint8_t *str, uint8_t index, char delimiter, uint8_t *result)
{
	// Find the field
	for (uint8_t i = 0; *str && (i < index); str++)
	{
		if ( *str == delimiter ) i ++;
	}
	
	// Copy the field
	uint8_t *p = result;
	for ( ; *str && *str != delimiter; p++, str ++)
	{
		*p = *str;
	}
	*p = '\0';
}



// Converts dddmm.mmmmm or ddmm.mmmmm to decimal degrees multiplied by 10000000
// Returns the decimal degrees or 0 in case of error
// Note: Position 0,0 is in the atlantic ocean, so no chance of conflict with the location

static int32_t convertDegreesMinutesToDegrees(uint8_t *str, uint8_t direction)
{
	int32_t ret;
	char fmt[15];
	uint32_t ddd, mm, mmmmm;

	// Create format to be either dddmm.mmmmm or ddmm.mmmmm depending on if it's latitude or longitude
	sprintf(fmt, "%%%dld%%2ld.%%5ld", (direction == 'W' || direction == 'E') ? 3 : 2);

	if ( sscanf((char *)str, fmt, &ddd, &mm, &mmmmm) == 3 )
	{
		// int32_t integer calculation convert mins to decimal degrees and adding to degrees
		// to avoid the use of floats
		int32_t mins = ((mm * 10000000) + (mmmmm * 100)) / 60;
		ret = ddd * 10000000 + mins;

		// Add sign
		if (direction == 'W' || direction == 'S')	ret = -ret;
		
		return ret;
	}

	return 0;
}



// We only process 3 sentances here, as they contain all the information we need
// Reference: https://content.u-blox.com/sites/default/files/products/documents/u-blox6-GPS-GLONASS-QZSS-V14_ReceiverDescrProtSpec_%28GPS.G6-SW-12013%29_Public.pdf

static void gpsProcessNmeaSentance(uint8_t *sentance)
{
	uint8_t field[15], direction[2];

	//DEBUG_STR((char *)sentance);
	//DEBUG_CHAR('\n');

	if	( zstrcmp( "$GPGGA", sentance) )
	{
		// $GPGGA,152253.00,5706.42309,N,11012.80644,W,1,08,1.08,1132.0,M,-17.5,M,,
		// GGA is in the deault WGS84 datum
		// 2 = latitude ddmm.mmmmmm
		// 3 = N or S
		// 4 = longitude dddmm.mmmmm
		// 5 = E or W
		// 7 = Number of satellite used for fix (00-12)
		// 9 = Altitude in m (above MSL)

		getField(sentance, 2, ',', field);
		getField(sentance, 3, ',', direction);
		gpsdata.latitude = convertDegreesMinutesToDegrees(field, direction[0]);

		getField(sentance, 4, ',', field);
		getField(sentance, 5, ',', direction);
		gpsdata.longitude = convertDegreesMinutesToDegrees(field, direction[0]);

		getField(sentance, 7, ',', field);
		gpsdata.satellites = (uint8_t)atoi((char *)field);

		int32_t altitude_major, altitude_minor;
		getField(sentance, 9, ',', field);
		if ( sscanf((char *)field, "%ld.%ld", &altitude_major, &altitude_minor) == 2 )
		{
			gpsdata.altitude = altitude_major * 10 + altitude_minor;
		}

		//char tmp[40];
		//sprintf(tmp, "Pos: %ld %ld %ld #%d\n", gpsdata.latitude, gpsdata.longitude, gpsdata.altitude, gpsdata.satellites);
		//DEBUG_STR(tmp);
		//DEBUG_CHAR('\n');
	}
	else if	( zstrcmp( "$GPGSA", sentance) )
	{
		// $GPGSA,A,3,17,24,19,25,03,06,12,11,,,,,2.01,1.08,1.70
		// 2 = Navigation Mode (1 = Fix not available, 2 = 2D Fix, 3 = 3D Fix)
		// 15 = Position dilution of precision(PDOP)
		// 16 = Horizontal dilution of precision(HDOP)
		// 17 = Vertical dilution of precision(VDOP)

		uint16_t major, minor;

		getField(sentance, 2, ',', field);
		if ( sscanf((char *)field, "%u", &major) == 1 )
		{
			gpsdata.fix = major;
		}

		getField(sentance, 15, ',', field);
		if ( sscanf((char *)field, "%u.%u", &major, &minor) == 2 )
		{
			gpsdata.pdop = major * 100 + minor; 
		}

		getField(sentance, 16, ',', field);
		if ( sscanf((char *)field, "%u.%u", &major, &minor) == 2 )
		{
			gpsdata.hdop = major * 100 + minor; 
		}

		getField(sentance, 17, ',', field);
		if ( sscanf((char *)field, "%u.%u", &major, &minor) == 2 )
		{
			gpsdata.vdop = major * 100 + minor; 
		}

		//char tmp[40];
		//sprintf(tmp, "Fix: %d DOP:P%d H%d V%d\n", gpsdata.fix, gpsdata.pdop, gpsdata.hdop, gpsdata.vdop);
		//DEBUG_STR(tmp);
	}
	else if	( zstrcmp( "$PUBX", sentance) )
	{
		// $PUBX,04,152253.00,270623,228172.99,2268,18,341699,401.278,21
		// 1 = Message ID (must be 04 for time)
		// 2 = Time hhmmss.ss
		// 3 = Date ddmmyy
		// 6 = Leap seconds (D = firmware default value)
		getField(sentance, 1, ',', field);
		if (strcmp((char *)field, "04") == 0)
		{
			getField(sentance, 2, ',', field);
			int16_t hour, min, sec, subsec, day, mon, year;
			sscanf((char *)field, "%02d%02d%02d.%02d", &hour, &min, &sec, &subsec);

			getField(sentance, 3, ',', field);
			sscanf((char *)field, "%02d%02d%02d", &day, &mon, &year);

			getField(sentance, 6, ',', field);
			char c;
			uint16_t leapSeconds;
			uint8_t leapSecondsDefault = 0;
			int n = sscanf((char *)field, "%d%c", &leapSeconds, &c);
			if ( n == 1 || n == 2 )
			{
				if ( n == 2 && c == 'D' )	leapSecondsDefault = 1;
			}

			struct tm tm;
			tm.tm_sec	= sec;
			tm.tm_min	= min;
			tm.tm_hour	= hour;
			tm.tm_mday	= day;
			tm.tm_mon	= mon-1;
			tm.tm_year	= year + 100;
			tm.tm_isdst	= 0;

			captureclockUpdateWithGPS(mktime(&tm) + UNIX_OFFSET, leapSeconds, leapSecondsDefault);

			// Write the gps spi registers
			gpsdata_buffers[gpsdata_write_index].latitude	= gpsdata.latitude;
			gpsdata_buffers[gpsdata_write_index].longitude	= gpsdata.longitude;
			gpsdata_buffers[gpsdata_write_index].altitude	= gpsdata.altitude;
			gpsdata_buffers[gpsdata_write_index].satellites	= gpsdata.satellites;
			gpsdata_buffers[gpsdata_write_index].fix	= gpsdata.fix;
			gpsdata_buffers[gpsdata_write_index].pdop	= gpsdata.pdop;
			gpsdata_buffers[gpsdata_write_index].hdop	= gpsdata.hdop;
			gpsdata_buffers[gpsdata_write_index].vdop	= gpsdata.vdop;
			gpsdata_read_index = gpsdata_write_index;
			gpsdata_write_index ++;
			gpsdata_write_index %= GPSDATA_MAX_BUFFERS;
		
			//char tmp[40];
			//sprintf(tmp, "%02d:%02d:%02d %02d/%02d/%02d Leap:%d(%d)\n", hour, min, sec, day, mon, year, leapSeconds, leapSecondsDefault);
			//DEBUG_STR(tmp);
		}
	}
}



// Converts a hex single character to a number

static uint8_t hexCharToDec(uint8_t ch)
{
	if	( ch >= '0' && ch <='9' )	return ch-'0';
	else if ( ch >= 'A' && ch <='F' )	return ch-'A'+10;
	return 0;
}



// Returns 1 if the sentance has a valid checksum and returns 0 if it doesn't
// If the checksum is valid, it removed the checksum from the asterisk onwards

static uint8_t gpsIsValidChecksumAndRemove(uint8_t *sentance)
{
	uint8_t xor = 0;
	uint8_t checksum;

	sentance ++; 	// $ gets ignored
	while ( *sentance && *sentance != '*' )
	{
		xor ^= *sentance;
		sentance ++;
	}

	if ( !(*sentance) )	return 0;

	if ( !(*(++sentance)) )	return 0;		// Skip * to first hex character
	checksum = hexCharToDec(*sentance) << 4;	// Read first hex character

	if ( !(*(++sentance)) )	return 0;		// Skip to 2nd hex character
	checksum |= hexCharToDec(*sentance);		// Read second hex character

	if ( checksum == xor )
	{
		sentance = sentance - 2;	// We delete the checksum and *
		*sentance = '\0';
		return 1;
	}
	
	return 0;
}



// Process all pending GPS messages
// Call this frequently

void gpsProcess(void)
{
	uint8_t ch;
	static uint8_t nmeaBufferSize = 0;
	static uint8_t nmeaBuffer[MAX_NMEA_MSG_SIZE + 2];
	static uint8_t firstValidSentance = 1;

	while ( usartGet(&ch) )
	{
		nmeaBuffer[nmeaBufferSize++] = ch;
		//DEBUG_CHAR(ch);

		// If buffer ends in CRLF or is full, it's complete, process
		if (nmeaBufferSize < 2) continue;

		if ( nmeaBufferSize > MAX_NMEA_MSG_SIZE )
		{
			DEBUG_STR("NMEA Buffer Overflow");
			DEBUG_CHAR('\n');
		}
		else if ( nmeaBuffer[nmeaBufferSize-2] == '\r' && nmeaBuffer[nmeaBufferSize-1] == '\n')
		{
			nmeaBuffer[nmeaBufferSize-2] = '\0';	// Terminate buffer (removing \r\n)
			if ( nmeaBuffer[0] == '$' && gpsIsValidChecksumAndRemove(nmeaBuffer) )
			{
				gpsProcessNmeaSentance(nmeaBuffer);

				if ( firstValidSentance )
				{
					firstValidSentance = 0;
					gpsMessageSetup();
				}
			}
			else
			{
				DEBUG_STR("Corrupt NMEA sentance: ");
				DEBUG_STR((char *)nmeaBuffer);
				DEBUG_CHAR('\n');
			}

			nmeaBufferSize = 0;
		}
	}
}
