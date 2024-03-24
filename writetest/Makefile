CC=/usr/bin/gcc
CFLAGS=-Os -Wall -D_FILE_OFFSET_BITS=64
TARGET=writetest
OBJS=writetest.o



all:	$(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET)

writetest.o: writetest.c
	$(CC) $(CFLAGS) -c writetest.c

install: all

distclean:	clean
		rm -f $(TARGET)	

clean:
	rm -f *.o
