#!/bin/env python3

import struct

catalog = '/media/pi/ASTRID/catalogs/daveherald/Gaia16_EDR3.bin'

#4521183636 Jan 25  2021  Gaia16_EDR3.bin	# OK, Format Read
#    519840 Jan 25  2021  Gaia16_EDR3.inx
#       627 Jan 25  2021  Gaia16_EDR3_Stats.txt
#    152592 Aug 31 16:35  GSC Fields.dat
#    481616 Jan 25  2021  Hipparcos_Gaia16_EDR3.dat
#   1299600 Aug 31 16:36  U4_Gaia14.inx

#[3145014, 0, 118379, 1966981, 2896, 3, 72718169, 0, 0]
# 0: 3145014 (Not matched, use star coords to identify)
# 1: 0 (Undefined)
# 2: 118379  (Hipparcos)
# 3: 1966981 (Tycho2-1 stars)
# 4: 2896 (Tycho2-2 stars)
# 5: 3 (Tycho2-3 stars
# 6: 72718169 (UCAC4)

#                Stars from Gaia : 77936526
#                TychoGaia stars : 2063800
#     Hipparcos not in TychoGaia : 24459
#           Matched to TychoGaia : 2054127
#           Added from TychoGaia : 9673
#           Matched to Hipparcos : 19216
#           Added from Hipparcos : 5243
# Has no proper motion from Gaia : 573122
#          Total number of stars : 77951442
#
#                          UCAC4
#                     Good match : 69146169
#                     Poor match : 3440703
#            Proper motion added : 131297
#                    Not matched : 3878620
#         Double matches removed : 237279



def read_entry(fp):
	RECORD_LEN = 58

	ret = {}

	record = fp.read(RECORD_LEN)
	if len(record) != RECORD_LEN:
		return None

	(ret['ra'], ret['ra2'], ret['dec'], ret['dec2'], ret['parallax'], ret['pm_ra'], ret['pm_dec'], ret['rv'], ret['epoch'], ret['mag_bp'], ret['mag_g'], ret['mag_rp'], ret['e_ra'], ret['e_dec'], ret['e_parx'], ret['e_pm_ra'], ret['e_pm_dec'], ret['e_rv'], ret['reliability_indicator'], ret['flags'], ret['star_diameter'], ret['g_version'], ret['source_id'], ret['cat_id'], ret['cat_num'])  = struct.unpack('=iBiBHiihhhhhHHHHHBBBBBQBI', record)
	return ret



fp = open(catalog, 'rb')

cat_types = [0,0,0,0,0,0,0,0,0]

record_num = 0

while True:
	if record_num % 100 == 0:
		print('\rRecord: %d' % record_num, end='')	

	record = read_entry(fp)
	if record is None:
		break
	else:
		#print('%d: %s' % (record_num, str(record)))
		cat_types[record['cat_id']] += 1
		a = True
	
	record_num += 1

fp.close()

print(cat_types)
