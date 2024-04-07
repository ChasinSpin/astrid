#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <sys/vfs.h>
#include <linux/magic.h>



#define EPOCH_MICROSECONDS	1000000

#define SEC_TO_US(sec)		((sec)*1000000)
#define NS_TO_US(ns)		((ns)/1000)

#define BYTES_PER_GB		(1024 * 1024 * 1024)

char fname[800];



void cleanup_file(void)
{
	unlink(fname);
}



void cleanup(int sig)
{
	cleanup_file();
	exit(1);
}



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



void writetest(char *fname, unsigned char *buf, size_t buf_size, float length)
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

	printf("\n--- START OF DATA ---\n");

	printf("Count,Total GB Transferred,Speed(MB/s),Text Version\n");
	fflush(stdout);

	long count = 0;

	while(1)
	{
		startTime = micros();
		written = write(fd, (void *)buf, buf_size);
		endTime = micros();

		if ( written < 0 )
		{
			printf("--- END OF DATA ---\n");
			perror("write");
			break;
		}
		else if ( written != (ssize_t)buf_size )
		{
			printf("--- END OF DATA ---\n");
			fprintf(stderr, "Short write: %d != %u\n", written, buf_size);
			break;
		}

		total_mb_transferred	+= (double)written / (double)(1024.0 * 1024.0);
		elapsed_time		= endTime - startTime;
		epoch_microseconds	+= elapsed_time;
		epoch_bytes		+= (uint64_t)written;

		gbTransferred =  total_mb_transferred / 1024.0;

		if ( gbTransferred >= length )
		{
			printf("--- END OF DATA ---\n");
			printf("Requested total of %0.3f GB transferred.\n", length);
			printf("Finished !\n");
			break;
		}

		if ( epoch_microseconds >= EPOCH_MICROSECONDS )
		{
			mbSpeed =  ((double)epoch_bytes / ((double)epoch_microseconds / (double)1000000.0)) / (1024.0 * 1024);
			
			printf("%ld,%0.4lf,%0.1lf,@%0.1lfGB transferred: write speed=%0.1lfMB/s\n", count, gbTransferred, mbSpeed, gbTransferred, mbSpeed);
			fflush(stdout);

			epoch_microseconds = 0;
			epoch_bytes = 0;
			count ++;
		}
	}

	close(fd);

	cleanup_file();
}



double free_space(char *drive)
{
	struct statfs statfsbuf;

	if (statfs(drive, &statfsbuf))
	{
		perror("statfs");
		exit(-3);
	}
	
	if ( statfsbuf.f_type != EXFAT_SUPER_MAGIC )
	{
		fprintf(stderr, "Error: FSType != ExFat\n");
		exit(-4);
	}

	//double gbTotal = (double)(statfsbuf.f_blocks * statfsbuf.f_bsize) / (double)BYTES_PER_GB;
	double gbFree  = (double)(statfsbuf.f_bavail * statfsbuf.f_bsize) / (double)BYTES_PER_GB;

	/*
		printf("FS type: 0x%X\n", statfsbuf.f_type);
		printf("FS bsize: %d\n", statfsbuf.f_bsize);
		printf("FS blocks: %llu\n", statfsbuf.f_blocks);
		printf("FS bfree: %llu\n", statfsbuf.f_bfree);
		printf("FS bavail: %llu\n", statfsbuf.f_bavail);
	*/

	//printf("GB Total: %0.3lf GB\n", gbTotal);
	printf("Available space on %s: %lf GB\n", drive, gbFree);

	return gbFree;
}



int main(int argc, char **argv)
{
	if ( argc != 4 )
	{
		fprintf(stderr, "Usage: %s blockSize(bytes) length(GB) drive\n", argv[0]);
		fprintf(stderr, "       e.g.: %s 2000000 30 /media/pi/ASTRID\n", argv[0]);
		exit(-1);
	}

	char *drive = argv[3];

	float length = atof(argv[2]);

	// Remove previous old test files hanging around
	sprintf(fname, "%s/iozone.test", drive); unlink(fname);
	sprintf(fname, "%s/longfile", drive); unlink(fname);

	float fspace = (float)free_space(drive);

	if ( fspace < (length + 0.5) )
	{
		fprintf(stderr, "Error: Not enough space to run test\n");
		exit(-4);
	}

	// Set the write file
	sprintf(fname, "%s/writetest_DELETEME_%d.dat", drive, getpid());

	signal(SIGINT, cleanup);
	signal(SIGHUP, cleanup);

	unsigned char *buf;
	size_t buf_size = atol(argv[1]);

	if ( (buf = createBuffer(buf_size)) == NULL )
	{
		perror("createBuffer");
		exit(2);
	}

	fflush(stdout);
	writetest(fname, buf, buf_size, length);

	free(buf);

	exit(0);
}
