// References:
//	https://docs.python.org/3/extending/extending.html
//		stdio.h, string.h errno.h and stdlib.h are defined by Python.h below
//
//	https://realpython.com/build-python-c-extension-module/

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <unistd.h>
#include <stdint.h>
#include <fcntl.h>
#include <time.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>


static int	spi_fd;
static uint8_t	spi_bpw = 8;
static uint32_t spi_speed;
static uint16_t spi_delay_us;



//#define DEBUG_TX_RX

#define RETRY_DELAY_US 100



// Arguments:
// 	unsigned int:		Device Major
// 	unsigned int: 		Device Minor
//	unsigned int:		Speed (MHz)
//	unsigned short int: 	Delay between bytes (and after last byte) in microseconds

static  PyObject *ospi_open(PyObject *self, PyObject *args)
{
	char deviceName[80+1];
	unsigned short int delay_us = 0;
	unsigned int devMajor = 0, devMinor = 0, speed = 2000000;

	if ( ! PyArg_ParseTuple(args, "IIIH", &devMajor, &devMinor, &speed, &delay_us) )	return NULL;

	sprintf(deviceName, "/dev/spidev%d.%d", devMajor, devMinor);

	spi_speed	= speed;
	spi_delay_us	= delay_us;

	if ( (spi_fd = open(deviceName, O_RDWR)) < 0 )
	{
		PyErr_SetFromErrnoWithFilename(PyExc_OSError, deviceName);
		return NULL;
	}

	Py_INCREF(Py_None);
	return Py_None;
}



// No arguments

static  PyObject *ospi_close(PyObject *self, PyObject *args)
{
	if ( ! PyArg_ParseTuple(args, "") ) return NULL;

	close(spi_fd);

	Py_INCREF(Py_None);
	return Py_None;
}



// Reference: https://www.nongnu.org/avr-libc/user-manual/group__util__crc.html

static uint8_t _crc8_ccitt_update (uint8_t inCrc, uint8_t inData)
{
	uint8_t	i;
	uint8_t	data;

	data = inCrc ^ inData;
	for ( i = 0; i < 8; i++ )
	{
		if (( data & 0x80 ) != 0 )
		{
			data <<= 1;
			data ^= 0x07;
		}
		else
		{
			data <<= 1;
		}
	}

	return data;
}



// Sends tx byte over SPI and reads rx byte simultaneously
// Return: 0=success, non-zero on error

static int xferByte(uint8_t tx, uint8_t *rx)
{
	uint8_t rxBuf[1];
	uint8_t txBuf[1];
	struct spi_ioc_transfer spi;

	// Setup the spi xfer
	memset (&spi, 0, sizeof(spi));
	txBuf[0]		= tx;
	spi.tx_buf		= (unsigned long)txBuf;
	spi.rx_buf		= (unsigned long)rxBuf;
	spi.len			= 1;
	spi.delay_usecs		= 0;
	spi.cs_change		= 0;	// Release Chip Select after transmission
	spi.speed_hz		= spi_speed;
	spi.bits_per_word	= spi_bpw;

	// Send
	int ret = ioctl(spi_fd, SPI_IOC_MESSAGE(1), &spi);

	*rx = rxBuf[0];

	return (ret != 1);
}



// Arguments
//	Type	Range		Description
//	----	-----		-----------
//	int	1-254	OTEStamper Command (cmd)
//	int	0-255	Read Length (number of bytes to read)
//	int	0-255	How many times to retry before failing
// Returns (Tuple):
//	int	0, 1	1 = Success, 0 = Failed due to retries exceeded
//	bytes	0-255	Data read
//	int	0-255	Retries (number of retries)
//	int		SPI execution time in microseconds
//	int 		hardware tx failures
//	int		crc failures


static  PyObject *ospi_cmd(PyObject *self, PyObject *args)
{
	uint8_t *rxBytes, rx, tx, crc, total_tx_len;
	uint8_t cmd, retries, success, readLen = 0;
	struct timespec start, end;
	uint8_t fail_hardware_tx, fail_crc;


	if ( ! PyArg_ParseTuple(args, "bbb", &cmd, &readLen, &retries) )	return NULL;

	clock_gettime(CLOCK_REALTIME, &start);

	if ( (rxBytes = (uint8_t *)malloc(readLen)) == NULL )
	{
		PyErr_NoMemory();	
		return NULL;
	}	

	total_tx_len = readLen + 1;

	uint8_t count_retries;
	fail_hardware_tx = 0;
	fail_crc = 0;
	for ( count_retries = 0; count_retries < retries; count_retries ++ )
	{
		success = 1;
		crc = 0x00;
		for ( uint8_t i = 0; i <= total_tx_len && success; i ++ )
		{
			if	( i == 0 )	
			{
				crc = _crc8_ccitt_update(crc, cmd);
				tx = cmd;
			}
			else if ( i == total_tx_len )	tx = 0x00;
			else				tx = 0xFF;
	
			if ( xferByte(tx, &rx) )
			{
				success = 0;
				fail_hardware_tx ++;
				//printf("xferBytes: failed transmission\n");
			}
			else
			{
				if ( i > 0 && i < total_tx_len )
				{
					rxBytes[i-1] = rx;
					crc = _crc8_ccitt_update(crc, rx);
				}
			}
			usleep(spi_delay_us);
		}

		// Validate the checksum
		if ( crc != rx )
		{
			success = 0;
			fail_crc ++;
			//printf("xferBytes: crc failed: 0x%02X != 0x%02X\n", rx, crc);
		}
		//else
		//{
		//	printf("xferBytes: crc matches: 0x%02X == 0x%02X\n", rx, crc);
		//}

		if ( success )	break;
	}
	if ( count_retries >= retries )
	{
		success = 0;
		printf("xferBytes: retries exceeded\n");
	}

	clock_gettime(CLOCK_REALTIME, &end);
	long int spi_execution_time = (end.tv_nsec-start.tv_nsec)/1000L;
	if ( spi_execution_time < 0L )	spi_execution_time += 1000000L;


	PyObject *res = Py_BuildValue("by#blbb", success, rxBytes, (Py_ssize_t)readLen, count_retries, spi_execution_time, fail_hardware_tx, fail_crc);

	free(rxBytes);
	
	return res;
}



static PyMethodDef OspiMethods[] = 
{
	{"open", ospi_open, METH_VARARGS, "Open SPI device"},
	{"close", ospi_close, METH_VARARGS, "Close SPI device"},
	{"cmd", ospi_cmd, METH_VARARGS, "Transfer to the SPI device"},
	{NULL, NULL, 0, NULL}
};



static struct PyModuleDef ospimodule = 
{
	PyModuleDef_HEAD_INIT,
	"ospi",				// Name of the module
	"OTEStamper SPI Interface",	// Module documentation (maybe NULL)
	-1,				// Size of per-interprete state of the module or -1 if the module keeps state in global variables
	OspiMethods
};



PyMODINIT_FUNC
PyInit_ospi(void)
{
	return PyModule_Create(&ospimodule);
}
