#!//usr/bin/env python3

from ravf import RavfReader, RavfWriter, RavfMetadataType, RavfFrameType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox

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
file_handle.close()
