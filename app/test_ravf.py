#!//usr/bin/env python3

from ravf import RavfReader, RavfWriter, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox

print('********* WRITER TEST ***********')
file_handle = open('movie.ravf', 'wb')

required_metadata_entries = [
    ('COLOR-TYPE',            int(RavfColorType.BAYER_BGGR.value)),
    ('IMAGE-ENDIANESS',       int(RavfImageEndianess.LITTLE_ENDIAN.value)),
    ('IMAGE-WIDTH',           int(1024)),
    ('IMAGE-HEIGHT',          int(768)),
    ('IMAGE-ROW-STRIDE',      int(2051)),
    ('IMAGE-FORMAT',          int(RavfImageFormat.FORMAT_16BIT.value)),
    ('FRAME-TIMING-ACCURACY', int(4)),
]

user_metadata_entries = [
    ('MY-USER-COMMENT', RavfMetadataType.UTF8STRING, 'This is a test comment'),
]

ravf = RavfWriter(file_handle = file_handle, required_metadata_entries = required_metadata_entries, user_metadata_entries = user_metadata_entries)

ravf.write_frame(file_handle, frame_type = RavfFrameType.LIGHT, data = b'\xA0\xB0\xC0\xD0', start_timestamp = 1000, exposure_duration = 50, satellites = 8, almanac_status = 0, almanac_offset = 1, satellite_fix_status = 3)
ravf.write_frame(file_handle, frame_type = RavfFrameType.LIGHT, data = b'RAVF', start_timestamp = 2000, exposure_duration = 100, satellites = 16, almanac_status = 1, almanac_offset = 2, satellite_fix_status = 1)

ravf.finish(file_handle)
file_handle.close()


print('\n\n\n\n\n')
print('********* READER TEST ***********')
file_handle = open('movie.ravf', 'rb')
ravf = RavfReader(file_handle = file_handle)
print('RAVF Version:', ravf.version())
print('Metadata:', ravf.metadata())
print('Timestamps:', ravf.timestamps())
print('Frame Count:', ravf.frame_count())
for i in range(ravf.frame_count()):
    frame = ravf.frame_by_index(file_handle, i)
    print(frame)
    print(frame.data)
file_handle.close()
