#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>



#define EPOCH_MICROSECONDS	1000000

#define SEC_TO_US(sec) ((sec)*1000000)
#define NS_TO_US(ns)    ((ns)/1000)



uint64_t micros()
{
	struct timespec ts;
	clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
	uint64_t us = SEC_TO_US((uint64_t)ts.tv_sec) + NS_TO_US((uint64_t)ts.tv_nsec);
	return us;
}


// Allocates a buffer of buf_size bytes and returns the buffer, or NULL in case of error
// Buffer needs to be free'd when finished with
// Buffer is initialized to random data

unsigned char *createBuffer(size_t buf_size)
{
	unsigned char *buf;

	if ( (buf = malloc(buf_size)) == NULL )	return NULL;

	long rl;
	unsigned char *r;
	r = (unsigned char *)&rl;

	for ( size_t i = 0; i < buf_size/4; i ++ )
	{	
		rl = random();
		bcopy((void *)r, (void *)(buf + i * 4), 4);
	}

	printf("Allocated random filled buffer: %u bytes\n", buf_size);

	return buf;
}



void writetest(char *fname, unsigned char *buf, size_t buf_size)
{
	int fd;

	fd = open(fname, O_CREAT | O_WRONLY | O_DSYNC | O_TRUNC);
	//fd = open(fname, O_CREAT | O_WRONLY | O_SYNC | O_TRUNC);
	//fd = open(fname, O_CREAT | O_WRONLY | O_TRUNC);

	if ( fd < 0 )
	{
		perror("open");
		exit(3);
	}

	ssize_t written;
	uint64_t startTime, endTime;

	double  total_mb_transferred = 0;
	uint64_t epoch_microseconds = 0, elapsed_time;
	uint64_t epoch_bytes = 0;

	double gbTransferred;
	double mbSpeed;

	printf("Total GB Transferred,Speed(MB/s),Text Version\n");

	while(1)
	{
		startTime = micros();
		written = write(fd, (void *)buf, buf_size);
		endTime = micros();

		if ( written < 0 )
		{
			perror("write");
			break;
		}
		else if ( written != (ssize_t)buf_size )
		{
			fprintf(stderr, "Short write: %d != %u\n", written, buf_size);
			//break;
		}

		total_mb_transferred	+= (double)written / (double)(1024.0 * 1024.0);
		elapsed_time		= endTime - startTime;
		epoch_microseconds	+= elapsed_time;
		epoch_bytes		+= (uint64_t)written;

		if ( epoch_microseconds >= EPOCH_MICROSECONDS )
		{
			gbTransferred =  total_mb_transferred / 1024.0;
			mbSpeed =  ((double)epoch_bytes / ((double)epoch_microseconds / (double)1000000.0)) / (1024.0 * 1024);
			
			printf("%0.1lf,%0.1lf,@%0.1lfGB transferred: write speed=%0.1lfMB/s\n", gbTransferred, mbSpeed, gbTransferred, mbSpeed);

			epoch_microseconds = 0;
			epoch_bytes = 0;
		}
	}

	close(fd);
}



int main(int argc, char **argv)
{
	if ( argc != 3 )
	{
		fprintf(stderr, "Usage: %s blockSize(bytes) filename\n", argv[0]);
		exit(-1);
	}

	unsigned char *buf;
	size_t buf_size = atol(argv[1]);

	if ( (buf = createBuffer(buf_size)) == NULL )
	{
		perror("createBuffer");
		exit(2);
	}

	printf("WARNING...  THIS WILL FILLUP THE FILESYSTEM UNTIL IT'S FULL!!\n");

	writetest(argv[2], buf, buf_size);

	free(buf);

	exit(0);
}
