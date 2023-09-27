#define GPSDATA_MAX_BUFFERS 3

struct __attribute__((__packed__)) gpsdata
{
        int32_t  latitude;      // Latitude in decimal degrees * 10000000
        int32_t  longitude;     // Longitude in decimal degrees * 10000000
        int32_t  altitude;      // Altitude in m (above MSL) * 10
        uint8_t  satellites;    // The number of satellites used in the fix
        uint8_t  fix;           // 0 = No gps packets received yet, 1 = Fix not available, 2 = 2D Fix, 3 = 3D Fix
        uint16_t pdop;          // Position dilution of precision * 100
        uint16_t hdop;          // Horizontal dilution of precision * 100
        uint16_t vdop;          // Vertical dilution of precision * 100
};

extern struct gpsdata gpsdata_buffers[GPSDATA_MAX_BUFFERS];
extern volatile uint8_t gpsdata_read_index;

extern void gpsInit(void);
extern void gpsColdStartReset(void);
extern void gpsProcess(void);
