#!/usr/bin/env python3

import sys
import numpy as np
from ravf import RavfReader, RavfImageUtils, RavfImageFormat, RavfMetadataType, RavfWriter, RavfFrameType



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
	return None


def usage():
	print('Usage: %s input.ravf output.ravf integration_frames(e.g. 2) average|sum' % sys.argv[0])
	sys.exit(-1)


if len(sys.argv) != 5:
	usage()

input_fname = sys.argv[1]
output_fname = sys.argv[2]
integration_frames = int(sys.argv[3])
if   sys.argv[4] == 'average':
	average = True
elif sys.argv[4] == 'sum':
	average = False
else:
	usage()

read_file_handle = open(input_fname, 'rb')
ravf_reader = RavfReader(file_handle = read_file_handle)

print('RAVF Version:', ravf_reader.version())
print('Metadata:', ravf_reader.metadata())
print('Timestamps:', ravf_reader.timestamps())
print('Frame Count:', ravf_reader.frame_count())

write_file_handle = open(output_fname, 'wb')

metadata = ravf_reader.metadata()

user_metadata_entries = [
	('INSTRUMENT-SENSOR-PIXEL-SIZE-X',      RavfMetadataType.FLOAT32,       getMetadata(metadata, 'INSTRUMENT-SENSOR-PIXEL-SIZE-X')[1]),
	('INSTRUMENT-SENSOR-PIXEL-SIZE-Y',      RavfMetadataType.FLOAT32,       getMetadata(metadata, 'INSTRUMENT-SENSOR-PIXEL-SIZE-X')[1]),
	('FOCAL-LENGTH',                        RavfMetadataType.FLOAT32,       getMetadata(metadata, 'FOCAL-LENGTH')[1]),
	('STATION-NUMBER',                      RavfMetadataType.UINT16,        getMetadata(metadata, 'STATION-NUMBER')[1]),
	('STATION-HOSTNAME',                    RavfMetadataType.UTF8STRING,    getMetadata(metadata, 'STATION-HOSTNAME')[1]),
	('INSTRUMENT-FRAMES-PER-SECOND',        RavfMetadataType.FLOAT32,       getMetadata(metadata, 'INSTRUMENT-FRAMES-PER-SECOND')[1] / float(integration_frames)),
	('INSTRUMENT-APERTURE',			RavfMetadataType.UINT16, 	getMetadata(metadata, 'INSTRUMENT-APERTURE')[1]),
	('INSTRUMENT-OPTICAL-TYPE',		RavfMetadataType.UTF8STRING, 	getMetadata(metadata, 'INSTRUMENT-OPTICAL-TYPE')[1]),
	('MY-USER-COMMENT',			RavfMetadataType.UTF8STRING,	'This ravf file has been integrated by: %dX' % integration_frames),
]

try:
	user_metadata_entries.append(('OCCULTATION-PREDICTED-CENTER-TIME',	RavfMetadataType.UTF8STRING, 	getMetadata(metadata, 'OCCULTATION-PREDICTED-CENTER-TIME')[1]))
except:
	pass

try:
	user_metadata_entries.append(('OCCULTATION-OBJECT-NUMBER',		RavfMetadataType.UTF8STRING, 	getMetadata(metadata, 'OCCULTATION-OBJECT-NUMBER')[1]))
except:
	pass

try:
	user_metadata_entries.append(('OCCULTATION-OBJECT-NAME',		RavfMetadataType.UTF8STRING, 	getMetadata(metadata, 'OCCULTATION-OBJECT-NAME')[1]))
except:
	pass

try:
	user_metadata_entries.append(('OCCULTATION-STAR',			RavfMetadataType.UTF8STRING, 	getMetadata(metadata, 'OCCULTATION-STAR')[1]))
except:
	pass

required_metadata = ravf_reader.metadata()
required_metadata = deleteMetadata(required_metadata, 'OFFSET-FRAMES')
required_metadata = deleteMetadata(required_metadata, 'OFFSET-INDEX')
required_metadata = deleteMetadata(required_metadata, 'FRAMES-COUNT')
required_metadata = deleteMetadata(required_metadata, 'OFFSET-FRAMES')
required_metadata = deleteMetadata(required_metadata, 'INSTRUMENT-SENSOR-PIXEL-SIZE-X')
required_metadata = deleteMetadata(required_metadata, 'INSTRUMENT-SENSOR-PIXEL-SIZE-Y')
required_metadata = deleteMetadata(required_metadata, 'FOCAL-LENGTH')
required_metadata = deleteMetadata(required_metadata, 'STATION-NUMBER')
required_metadata = deleteMetadata(required_metadata, 'STATION-HOSTNAME')
required_metadata = deleteMetadata(required_metadata, 'INSTRUMENT-FRAMES-PER-SECOND')
required_metadata = deleteMetadata(required_metadata, 'OCCULTATION-PREDICTED-CENTER-TIME')
required_metadata = deleteMetadata(required_metadata, 'OCCULTATION-PREDICTED-CENTER-TIME')
required_metadata = deleteMetadata(required_metadata, 'OCCULTATION-OBJECT-NUMBER')
required_metadata = deleteMetadata(required_metadata, 'OCCULTATION-OBJECT-NAME')
required_metadata = deleteMetadata(required_metadata, 'OCCULTATION-STAR')
required_metadata = deleteMetadata(required_metadata, 'INSTRUMENT-APERTURE')
required_metadata = deleteMetadata(required_metadata, 'INSTRUMENT-OPTICAL-TYPE')
required_metadata = deleteMetadata(required_metadata, 'MY-USER-COMMENT')

required_metadata = setMetadata(required_metadata, 'IMAGE-FORMAT', int(RavfImageFormat.FORMAT_16BIT.value))
required_metadata = setMetadata(required_metadata, 'IMAGE-ROW-STRIDE', getMetadata(metadata, 'IMAGE-WIDTH')[1] * 2)

print(user_metadata_entries)

ravf_writer = RavfWriter(file_handle = write_file_handle, required_metadata_entries = required_metadata, user_metadata_entries = user_metadata_entries )

for i in range(int(ravf_reader.frame_count()/integration_frames)):
	errs = []
	images = []
	frameInfos = []
	statuses = []

	total_exposure_duration = 0

	for f in range(integration_frames):
		current_index = (i * integration_frames) + f
		#print('Loading:', current_index)
		(err, image, frameInfo, status) = ravf_reader.getPymovieMainImageAndStatusData(read_file_handle, current_index)

		#print('Image light range: %d..%d' % (np.min(image), np.max(image)))
		image = image.astype(np.float32);
		image /= 65535.0	# Change to 0-1
		print('Status:', status);
		total_exposure_duration += status['exposure_duration']

		errs.append(err)
		images.append(image.copy())
		frameInfos.append(frameInfo)
		statuses.append(status)

	# Integrate the images by summing them
	integrated_image = images[0]
	for f in range(1,integration_frames):
		#print('Image %d light range: %f..%f' % (f, np.min(integrated_image), np.max(integrated_image)))
		integrated_image = np.add(integrated_image, images[f])

	# Average or if we're summing, we clip
	if average:
		integrated_image = np.divide(integrated_image, float(integration_frames))
	else:
		# Clip
		integrated_image = np.clip(integrated_image, 0.0, 1.0)

	# Switch back to uint16 0-65535
	integrated_image = (integrated_image * 65535.0).astype(np.uint16)

	integrated_image = integrated_image.tobytes()

	ravf_writer.write_frame( write_file_handle,
		frame_type = RavfFrameType.LIGHT,
		data = integrated_image,
		start_timestamp = statuses[0]['start_timestamp'],
		exposure_duration = total_exposure_duration,
		satellites = statuses[0]['satellites'],
		almanac_status = statuses[0]['almanac_status'],
		almanac_offset = statuses[0]['almanac_offset'],
		satellite_fix_status = statuses[0]['satellite_fix_status'],
		sequence = statuses[0]['sequence'])

read_file_handle.close()

ravf_writer.finish(write_file_handle)
write_file_handle.close()
