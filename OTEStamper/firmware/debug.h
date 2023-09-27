#ifdef DEBUG

extern void debugInit(void);
extern void debugChar(unsigned char ch);
extern void debugHex(uint8_t x);
extern void debugHex32(uint32_t x);
extern void debugDecU32(uint32_t v, uint8_t display_leading_zeros, uint8_t dp);
extern void debugDecS32(int32_t v, uint8_t display_leading_zeros, uint8_t dp);
extern void debugStr(char *str);

#define DEBUG_INIT		debugInit()
#define DEBUG_CHAR(x)		debugChar((x))
#define DEBUG_HEX(x)		debugHex((x))
#define DEBUG_HEX32(x)		debugHex32((x))
#define DEBUG_DECU32(x,z, d)	debugDecU32((x), (z), (d))
#define DEBUG_DECS32(x,z, d)	debugDecS32((x), (z), (d))
#define DEBUG_STR(x)		debugStr((x))

#else

#define DEBUG_INIT
#define DEBUG_CHAR(x)
#define DEBUG_HEX(x)
#define DEBUG_HEX32(x)
#define DEBUG_DECU32(x, z, d)
#define DEBUG_DECS32(x, z, d)
#define DEBUG_STR(x)

#endif
