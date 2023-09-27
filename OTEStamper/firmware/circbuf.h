struct circbuf
{
	volatile uint8_t start;
	volatile uint8_t end;
	uint8_t *buf;
	uint8_t len;
};


extern void circbuf_create(struct circbuf *cbuf, uint8_t *buffer, uint8_t len);
extern uint8_t circbuf_put(struct circbuf *cbuf, uint8_t item);
extern uint8_t circbuf_get(struct circbuf *cbuf, uint8_t *item);
