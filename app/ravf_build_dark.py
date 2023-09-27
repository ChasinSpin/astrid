#!/usr/bin/env python3

import sys
import numpy as np
from ravf import RavfReader, RavfImageUtils, RavfImageFormat, RavfMetadataType, RavfWriter, RavfFrameType

offset = 33000		# Subtract this from the resulting output frames, before multiplying by 2 so 0-1023 resolution isn't lost
binFactor = 1		# Rebin by this factor



def setMetadata(metadata, key, obj):
	nmetadata = []

	for kv in metadata:
		if kv[0] == key:
			nmetadata.append((kv[0], obj))
		else:
			nmetadata.append(kv)

	return nmetadata


def deleteMetadata(metadata, key):
	nmetadata = []

	for kv in metadata:
		if kv[0] != key:
			nmetadata.append(kv)
	return nmetadata


def getMetadata(metadata, key):
	for kv in metadata:
		if kv[0] == key:
			return kv



# Reference: https://scipython.com/blog/binning-a-2d-array-in-numpy/

def rebin(arr, new_shape):
	"""Rebin 2D array arr to shape new_shape by averaging."""
	shape = (new_shape[0], arr.shape[0] // new_shape[0],
		new_shape[1], arr.shape[1] // new_shape[1])
	return arr.reshape(shape).mean(-1).mean(1)



if len(sys.argv) != 3 and len(sys.argv) != 4:
	print('Usage: %s light.ravf out.ravf [dark.ravf]' % sys.argv[0])
	sys.exit(-1)

light_fname = sys.argv[1]
out_fname = sys.argv[2]
if len(sys.argv) == 4:
	dark_fname = sys.argv[3]
else:
	dark_fname = None


if dark_fname is not None:
	dark_file_handle = open(dark_fname, 'rb')

	ravf = RavfReader(file_handle = dark_file_handle)
	print('RAVF Version:', ravf.version())
	print('Metadata:', ravf.metadata())
	print('Timestamps:', ravf.timestamps())
	print('Frame Count:', ravf.frame_count())

	stride = ravf.metadata_value('IMAGE-ROW-STRIDE')
	height = ravf.metadata_value('IMAGE-HEIGHT')
	width = ravf.metadata_value('IMAGE-WIDTH')
	format = ravf.metadata_value('IMAGE-FORMAT')

	image_accumulator = None

	for i in range(ravf.frame_count()):
		#frame = ravf.frame_by_index(dark_file_handle, i)
		print('\rProcessing dark frame:', i, end='')
		(err, image, frameInfo, status) = ravf.getPymovieMainImageAndStatusData(dark_file_handle, i)
	
		if image_accumulator is None:
			image_accumulator = image.astype(np.float32)
		else:
			image_accumulator += image.astype(np.float32)
		image_accumulator /= 65535.0	# Change to 0-1

	dark_frame = image_accumulator / float(ravf.frame_count())

	print('\nMaster dark range: %0.3f..%0.3f' % (np.min(dark_frame), np.max(dark_frame)))

	dark_file_handle.close()
else:
	dark_frame = None


read_file_handle = open(light_fname, 'rb')
ravf_reader = RavfReader(file_handle = read_file_handle)

print('RAVF Version:', ravf_reader.version())
print('Metadata:', ravf_reader.metadata())
print('Timestamps:', ravf_reader.timestamps())
print('Frame Count:', ravf_reader.frame_count())

stride = ravf_reader.metadata_value('IMAGE-ROW-STRIDE')
orig_height = ravf_reader.metadata_value('IMAGE-HEIGHT')
orig_width = ravf_reader.metadata_value('IMAGE-WIDTH')
format = ravf_reader.metadata_value('IMAGE-FORMAT')

write_file_handle = open(out_fname, 'wb')
user_metadata_entries = [
	('MY-USER-COMMENT', RavfMetadataType.UTF8STRING, 'This is a test comment')
]

required_metadata = ravf_reader.metadata()
required_metadata = deleteMetadata(required_metadata, 'OFFSET-FRAMES')
required_metadata = deleteMetadata(required_metadata, 'OFFSET-INDEX')
required_metadata = deleteMetadata(required_metadata, 'FRAMES-COUNT')
required_metadata = deleteMetadata(required_metadata, 'MY-USER-COMMENT')
required_metadata = setMetadata(required_metadata, 'IMAGE-FORMAT', int(RavfImageFormat.FORMAT_16BIT.value))

if binFactor == 1:
	new_height = orig_height
	new_width = orig_width
else:
	new_height = int(orig_height / binFactor)
	new_width = int(orig_width / binFactor)

print('NewWidth:', new_width)
print('NewHeight:', new_height)

required_metadata = setMetadata(required_metadata, 'IMAGE-ROW-STRIDE', new_width * 2)
required_metadata = setMetadata(required_metadata, 'IMAGE-WIDTH', new_width)
required_metadata = setMetadata(required_metadata, 'IMAGE-HEIGHT', new_height)

print(user_metadata_entries)

ravf_writer = RavfWriter(file_handle = write_file_handle, required_metadata_entries = required_metadata, user_metadata_entries = user_metadata_entries )

for i in range(ravf_reader.frame_count()):
	(err, image, frameInfo, status) = ravf_reader.getPymovieMainImageAndStatusData(read_file_handle, i)

	image = image.astype(np.float32)
	image /= 65535.0	# Change to 0-1
	#print('Image light range: %d..%d' % (np.min(image), np.max(image)))

	if dark_frame is not None:
		calibrated_image = ((image - dark_frame) + 1.0) / 2.0
	else:
		calibrated_image = image


	calibrated_image = (calibrated_image * 65535.0).astype(np.uint16)

	if dark_frame is not None:
		calibrated_image_offset_scaled = (calibrated_image - offset) * 2
	else:
		calibrated_image_offset_scaled = calibrated_image

	print('Calibrated %d light range: %d..%d -> %d..%d' % (i, np.min(calibrated_image), np.max(calibrated_image), np.min(calibrated_image_offset_scaled), np.max(calibrated_image_offset_scaled)))

	if binFactor != 1:
		calibrated_image_offset_scaled = rebin(calibrated_image_offset_scaled, (new_height, new_width)).astype(np.uint16)
	calibrated_image_offset_scaled = calibrated_image_offset_scaled.tobytes()

	ravf_writer.write_frame( write_file_handle,
		frame_type = RavfFrameType.LIGHT,
		data = calibrated_image_offset_scaled,
		start_timestamp = status['start_timestamp'],
		exposure_duration = status['exposure_duration'],
		satellites = status['satellites'],
		almanac_status = status['almanac_status'],
		almanac_offset = status['almanac_offset'],
		satellite_fix_status = status['satellite_fix_status'],
		sequence = status['sequence'])

read_file_handle.close()

ravf_writer.finish(write_file_handle)
write_file_handle.close()
