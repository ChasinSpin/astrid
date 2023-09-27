#include "config.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include "circbuf.h"
#include "debug.h"
#include "usart.h"



#define USART_BAUD_RATE 9600

#define USART_RX_BUF_LEN 254
static struct circbuf cb_usart_rx;
static uint8_t buf_usart_rx[USART_RX_BUF_LEN];

#define USART_TX_BUF_LEN 254
static struct circbuf cb_usart_tx;
static uint8_t buf_usart_tx[USART_TX_BUF_LEN];


// Baud Rate 9600 @ F_CPU of 8MHz
#define USART_UBRR0H	0
#define USART_UBRR0L	51



// Initialize the USART

void usartInit(void)
{
	// Create circular buffers to hold rx and tx characters
        circbuf_create(&cb_usart_rx, buf_usart_rx, USART_RX_BUF_LEN);
        circbuf_create(&cb_usart_tx, buf_usart_tx, USART_TX_BUF_LEN);

	cli();	// Disable interrupts Requirement during setup according to datasheet

	// Set Baud rate
	UBRR0H = (uint8_t)USART_UBRR0H;
	UBRR0L = (uint8_t)USART_UBRR0L;

	// Set frame format 8N1
	UCSR0C = _BV(USBS0) | _BV(UCSZ01) | _BV(UCSZ00);

	// Enable receiver and transmitter
	UCSR0B = _BV(RXEN0) | _BV(TXEN0);

	// Setup interrupts
	UCSR0B |= _BV(TXCIE0) | _BV(RXCIE0);
}



// Returns 1 if buffer contains data and 0 if it's empty

uint8_t usartGet(uint8_t *ch)
{
	return circbuf_get(&cb_usart_rx, ch);
}



// Returns 0 if the item was put in the  buffer and 1 if it was full

uint8_t usartPut(uint8_t ch)
{
	if ( circbuf_put(&cb_usart_tx, ch) )
	{
		DEBUG_STR("TXBuf Full\n");
		return 1;
	}

	if ( UCSR0A & _BV(UDRE0) )
	{
		uint8_t tx;
		if ( circbuf_get(&cb_usart_tx, &tx) )
		{
			UDR0 = tx;
		}
	}
	
	return 0;
}



// Returns 0 if the string was put in the buffer or 1 if it became full during transmission

uint8_t usartPutStr(char *str)
{
	char *p;

	p = str;
	while (*p)
	{
		if ( usartPut(*p++) )	return 1;
	}

	return 0;
}



// Returns 0 if the data was put in the buffer or 1 if it became full during transmission

uint8_t usartPutData(uint8_t *data, uint8_t len)
{
        for (uint8_t i = 0; i < len; i ++ )
        {
		if ( usartPut(data[i]) )	return 1;
        }

	return 0;
}



// USART RX Complete Interrupt

ISR(USART0_RX_vect)
{
	static uint8_t ch;
	static uint8_t status;

	status = UCSR0A;	// Read the status
	ch = UDR0;		// Read the data

	// Add to the buffer
	if ( circbuf_put(&cb_usart_rx, ch) )
		DEBUG_STR("usartRxFull");

	// Process error
	if ( status & _BV(FE0) )
		DEBUG_STR("EFE\n");
	else if ( status & _BV(DOR0) )
		DEBUG_STR("EDOR\n");
	else if ( status & _BV(UPE0) )
		DEBUG_STR("EUPE\n");
}



// USART TX Complete Interrupt

ISR(USART0_TX_vect)
{
	static uint8_t ch;
	static uint8_t status;

	status = UCSR0A;	// Read the status

	// Only send if buffer is ready
	if ( status & _BV(UDRE0) )
	{
		if ( circbuf_get(&cb_usart_tx, &ch) )	UDR0 = ch;
	}
}
