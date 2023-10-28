MCU=atmega328pb
AVRDUDEMCU=m328pb
FUSES=-U lfuse:w:0xF7:m -U hfuse:w:0xDA:m -U efuse:w:0x06:m
#FUSES=-U lfuse:w:0x62:m -U hfuse:w:0xD9:m -U efuse:w:0x07:m	# DEFAULT ATmega328p shipping fuses
CC=/usr/bin/avr-gcc
CFLAGS=-g -Os -Wall -mcall-prologues -mmcu=$(MCU)
OBJ2HEX=/usr/bin/avr-objcopy
AVRDUDE=/usr/local/bin/avrdude
TARGET=otestamper
OBJS=otestamper.o circbuf.o spi.o usart.o buzzer.o debug.o led.o fan.o captureclock.o gps.o eeprom.o frameinterrupt.o voltage.o



all:	$(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET)
	$(OBJ2HEX) -R .eeprom -O ihex $(TARGET) $(TARGET).hex
	rm -f $(TARGET)

otestamper.o: otestamper.c config.h debug.h spi.h usart.h buzzer.h led.h fan.h captureclock.h gps.h eeprom.h frameinterrupt.h voltage.h
	$(CC) $(CFLAGS) -c otestamper.c

circbuf.o: circbuf.c circbuf.h
	$(CC) $(CFLAGS) -c circbuf.c

spi.o: spi.c spi.h debug.h captureclock.h led.h fan.h buzzer.h gps.h config.h
	$(CC) $(CFLAGS) -c spi.c

usart.o: usart.c usart.h debug.h config.h
	$(CC) $(CFLAGS) -c usart.c

buzzer.o: buzzer.c buzzer.h debug.h config.h
	$(CC) $(CFLAGS) -c buzzer.c

debug.o: debug.c debug.h circbuf.h usart.h config.h
	$(CC) $(CFLAGS) -c debug.c

led.o: led.c led.h debug.h config.h
	$(CC) $(CFLAGS) -c led.c

fan.o: fan.c fan.h debug.h config.h
	$(CC) $(CFLAGS) -c fan.c

captureclock.o: captureclock.c captureclock.h debug.h config.h eeprom.h spi.h led.h frameinterrupt.h
	$(CC) $(CFLAGS) -c captureclock.c

gps.o: gps.c gps.h debug.h config.h captureclock.h spi.h
	$(CC) $(CFLAGS) -c gps.c

eeprom.o: eeprom.c eeprom.h debug.h config.h
	$(CC) $(CFLAGS) -c eeprom.c

frameinterrupt.o: frameinterrupt.c frameinterrupt.h config.h
	$(CC) $(CFLAGS) -c frameinterrupt.c

voltage.o: voltage.c voltage.h config.h
	$(CC) $(CFLAGS) -c voltage.c

debug.h:

circbuf.h:

spi.h:

buzzer.h:

usart.h:

led.h:

fan.h:

captureclock.h:

gps.h:

eeprom.h:

frameinterrupt.h:

voltage.h:

install: all
	raspi-gpio set 22 op
	raspi-gpio set 22 dl	# Reset - put in programming mode
	sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 500000 -U flash:w:$(TARGET).hex
	raspi-gpio set 22 dh

reset:
	raspi-gpio set 22 op
	raspi-gpio set 22 dl	# Reset - put in programming mode
	sleep 0.5
	raspi-gpio set 22 dh


readfuses:
	sudo raspi-gpio set 22 op
	sudo raspi-gpio set 22 dl
	sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000
	sudo raspi-gpio set 22 dh

writefuses:
	sudo raspi-gpio set 22 op
	sudo raspi-gpio set 22 dl
	sudo $(AVRDUDE) -p $(AVRDUDEMCU) -P /dev/spidev0.0 -c linuxspi -b 10000 $(FUSES)
	sudo raspi-gpio set 22 dh

clean :
	rm -f *.hex *.obj *.o
