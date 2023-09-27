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




// Arguments:
// 	unsigned int:		Device Major
// 	unsigned int: 		Device Minor
//	unsigned int:		Speed (MHz)
//	unsigned short int: 	Delay between bytes (and after last byte) in microseconds

static  PyObject *oteutils_open(PyObject *self, PyObject *args)
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

static  PyObject *oteutils_close(PyObject *self, PyObject *args)
{
	if ( ! PyArg_ParseTuple(args, "") ) return NULL;

	close(spi_fd);

	Py_INCREF(Py_None);
	return Py_None;
}



// Sends tx byte over SPI and reads rx byte simultaneously
// butWaitTheresMore = 1: Hold Chip Select Active after transmission, 0 = release Chip Select (Sequential transactions)
// Return: 0=success, non-zero on error

static int spiXferByte(uint8_t tx, uint8_t *rx, int butWaitTheresMore)
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
	spi.delay_usecs		= spi_delay_us;
	spi.cs_change		= butWaitTheresMore;
	spi.speed_hz		= spi_speed;
	spi.bits_per_word	= spi_bpw;

	// Send
	int ret = ioctl(spi_fd, SPI_IOC_MESSAGE(1), &spi);

	*rx = rxBuf[0];

	return ret;
}



//Arguments
//	Bytes:	Bytes to send
//Returns:
//	Bytes read during the transfer


static  PyObject *oteutils_xfer(PyObject *self, PyObject *args)
{
	Py_ssize_t len;
	uint8_t *rxBytes;
	const uint8_t *txBytes;
	struct timespec start, end;

	clock_gettime(CLOCK_REALTIME, &start);

	if ( ! PyArg_ParseTuple(args, "y#", &txBytes, &len) )	return NULL;

	if ( (rxBytes = (uint8_t *)malloc(len)) == NULL )
	{
		PyErr_NoMemory();	
		return NULL;
	}	

	// Send the data
	for ( int i = 0; i < len; i ++ )
		spiXferByte(txBytes[i], &rxBytes[i], (i == (len-1)) ? 0 : 1);

	// Debugging
	//printf("Len: %u\n", len);
	//for ( int i = 0; i < len; i ++ )
	//	printf("0x%02X\n", txBytes[i]);

	// Return the receive byte array
	PyObject *res = Py_BuildValue("y#", rxBytes, len);
	free(rxBytes);

	clock_gettime(CLOCK_REALTIME, &end);
	printf("%ldus\n", (end.tv_nsec-start.tv_nsec)/1000L);

	return res;
}



static PyMethodDef OTEUtilsMethods[] = 
{
	{"spiOpen",	oteutils_open,  METH_VARARGS, "Open SPI device"},
	{"spiClose",	oteutils_close, METH_VARARGS, "Close SPI device"},
	{"spiXfer",  	oteutils_xfer,  METH_VARARGS, "Transfer SPI data"},
	{NULL, NULL, 0, NULL}
};



static struct PyModuleDef oteutilsmodule = 
{
	PyModuleDef_HEAD_INIT,
	"oteutils",			// Name of the module
	"Utils for OTERecorder",	// Module documentation (maybe NULL)
	-1,				// Size of per-interprete state of the module or -1 if the module keeps state in global variables
	OTEUtilsMethods
};



PyMODINIT_FUNC
PyInit_oteutils(void)
{
	return PyModule_Create(&oteutilsmodule);
}
