enum captureClockStatus
{
	CC_STATUS_UNKNOWN			= 0,
	CC_STATUS_PPS_SEEN			= _BV(0),	// Set if time based on PPS has been seen since startup
	CC_STATUS_PPS_RECENT			= _BV(1),	// Set if 2 PPS pulses have been received within the last 2 seconds
	CC_STATUS_LEAP_SECONDS_SOURCE_GPS	= _BV(2),       // Only when GPS knows it's leap seconds, not when it's using firmware default (D).  This is the normal operating mode
	CC_STATUS_LEAP_SECONDS_SOURCE_EEPROM	= _BV(3),       // Leap seconds are coming from the eeprom and a previous run
	CC_STATUS_LEAP_SECONDS_SOURCE_SOFTWARE	= _BV(4),       // Eeprom doesn't contain the leap seconds, and they are coming from LEAP_SECONDS_SOFTWARE_DEFAULT
	CC_STATUS_TIME_JUMPED			= _BV(5)        // Set if the time jumped, flag is reset when status is read by host system
};

#define CC_STATUS_SUMMARY_TIME_ACCURATE		(CC_STATUS_PPS_SEEN | CC_STATUS_PPS_RECENT | CC_STATUS_LEAP_SECONDS_GPS)	// Everything is good
#define CC_STATUS_SUMMARY_TIME_AVAILABLE	(CC_STATUS_PPS_SEEN | CC_STATUS_PPS_RECENT)					// Time is available, it's likely good but may have a leap second error
#define CC_STATUS_LEAP_SECONDS_SOURCE_MSK	(CC_STATUS_LEAP_SECONDS_SOURCE_GPS | CC_STATUS_LEAP_SECONDS_SOURCE_EEPROM | CC_STATUS_LEAP_SECONDS_SOURCE_SOFTWARE)


#define FRAME_INFO_QUEUE_MAX 10

struct __attribute__((__packed__)) frameInfoQueueEntry
{
	uint8_t		queue_size;	// Remaining frame info's in queue, 1 = current entry, 0 = empty queue (in which case this item is not entry)
	int8_t		leapSeconds;
	uint8_t		clockStatus;
	uint8_t		frame_sequence;
	uint32_t	last_pps_duration;
	uint32_t	frame_ticks_since_last_pps;
	uint32_t	frame_unix_epoch;
};

extern struct frameInfoQueueEntry frameInfoQueue[FRAME_INFO_QUEUE_MAX];
extern volatile uint8_t frame_info_queue_read_index;
extern uint8_t frame_info_queue_write_index;
extern volatile uint8_t frame_info_queue_size;

extern volatile time_t	systemtime_secs;
extern volatile uint8_t capture_clock_status;
extern int8_t		leapSeconds;

extern void captureclockInit(void);
extern int32_t captureclockSystemTimeSecondOffset(void);
extern uint8_t captureclockStatus(void);
#ifdef DEBUG
extern void captureclockHandler(void);
#endif
extern void testTimingEnable(uint8_t enable);
extern void captureclockUpdateWithGPS(time_t gpsTime, int8_t gpsLeapSeconds, uint8_t gpsLeapSecondsFirmwareDefault);
extern void setFrameInterruptEnabled(uint8_t enabled);
extern void captureclock_interrupt_pps(void);
extern void captureclock_interrupt_xvs(void);
extern void captureclock_timer_overflow_interrupt(void);
