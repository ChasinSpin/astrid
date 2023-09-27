#include <avr/io.h>
#include "circbuf.h"



// Creates a circular buffer.  Buffers are limited to 254 bytes in size and the buffer can only ever store upto 1 byte less (so that full can be detected)
// 	cbuf - A preallocated statically allocated circbuf structure that will contain information about the buffer, this will be overwritten
//	buffer - A statically allocated buffer of size len
//	len - The size of the buffer

void circbuf_create(struct circbuf *cbuf, uint8_t *buffer, uint8_t len)
{
	cbuf->len	= len;
	cbuf->buf	= buffer;
	cbuf->start	= cbuf->end = 0;
}



// Puts an item in the circular buffer
// Returns 0 if inserted okay and 1 if buffer is full

uint8_t circbuf_put(struct circbuf *cbuf, uint8_t item)
{
	if (((cbuf->end + 1) % cbuf->len) == cbuf->start )	return 1; // Buffer full

	cbuf->buf[cbuf->end++]	=  item;
	cbuf->end	 	%= cbuf->len;

	return 0;
}



// Gets an item from the circular buffer and puts it in item
// Returns 1 if successful or 0 if buffer is empty

uint8_t circbuf_get(struct circbuf *cbuf, uint8_t *item)
{
	if ( cbuf->start == cbuf->end )	return 0; // Empty

	*item =  cbuf->buf[cbuf->start++];
	cbuf->start  %= cbuf->len;

	return 1;
}
