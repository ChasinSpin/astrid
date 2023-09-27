#!/usr/bin/env python3

from simpleadv2 import SimpleAdv2Writer, SimpleAdv2StreamConfig, SimpleAdv2Stream, SimpleAdv2Compression, SimpleAdv2StatusDataType, SimpleAdv2DataLayout

system_tags = [
    ('RECORDER-SOFTWARE', 'Astrid'),
    ('RECORDER-SOFTWARE-VERSION', '0.1.1234.0'),
    ('RECORDER-HARDWARE', 'Astrid'),
    ('RECORDER-HARDWARE-VERSION', '0.9'),
    ('CAMERA-MODEL', 'RASPBERRY PI GS'),
    ('CAMERA-SERIAL-NO', '00000000'),
    ('CAMERA-VENDOR-NAME', 'I made this'),
    ('CAMERA-SENSOR-INFO', 'IMX296LQR-C'),
    ('CAMERA-DRIVER-NAME', 'Astrid'),
    ('CAMERA-DRIVER-VERSION', '0.1'),
    ('LATITUDE', '51.00000000'),
    ('LONGITUDE', '-113.00000000'),
    ('ALTITUDE', '500.0'),
    ('BINNING-X', '1'),
    ('BINNING-Y', '1'),
    ('AUTHOR', '@ChasinSpin'),
    ('COMMENT', 'Test file'),
    ('EPOCH', 'J2000'),
    ('EQUINOX', 'J2000'),
    ('INSTRUMENT', 'Dominator Observatory'),
    ('OBSERVER', 'Mark Simpson'),
    ('TELESCOPE', 'Redcat 71'),
    ('RA', '200.389238423'),
    ('DEC', '72.38983245'),
    ('OBJNAME', 'M101'),
    ('ADV-VERSION', '2'),
    ('BITPIX', '12'),
    ('FSTF-TYPE', 'ADV'),
    ('WIDTH', '1024'),
    ('HEIGHT', '768'),
]

status_variables = [
    ('Gain',                 SimpleAdv2StatusDataType.REAL),
    ('Shutter',              SimpleAdv2StatusDataType.REAL),
    ('Offset',               SimpleAdv2StatusDataType.REAL),
    ('SystemTime',           SimpleAdv2StatusDataType.INT64),
    ('VideoCameraFrameId',   SimpleAdv2StatusDataType.INT32),
    ('HardwareTimerFrameId', SimpleAdv2StatusDataType.INT32),
    ('TrackedSatellites',    SimpleAdv2StatusDataType.INT8),
    ('AlmanacStatus',        SimpleAdv2StatusDataType.INT8),
    ('AlmanacOffset',        SimpleAdv2StatusDataType.INT8),
    ('SatelliteFixStatus',   SimpleAdv2StatusDataType.INT8),
    ('Error',                SimpleAdv2StatusDataType.UTF8STRING),
]

image_stream_config = SimpleAdv2StreamConfig(bits_per_pixel = 12, data_layout = SimpleAdv2DataLayout.IMAGE_FULL_RAW, clock_frequency = 10000000, clock_accuracy = 0, compression = SimpleAdv2Compression.UNCOMPRESSED, regions_of_interest = None)
calibration_stream_config = SimpleAdv2StreamConfig(bits_per_pixel = 12, data_layout = SimpleAdv2DataLayout.IMAGE_FULL_RAW, clock_frequency = 10000000, clock_accuracy = 0, compression = SimpleAdv2Compression.UNCOMPRESSED, regions_of_interest = None)

adv_writer = SimpleAdv2Writer(filename                       = 'test2.adv',
                              dimensions                     = (720, 540),
                              native_bits_per_pixel          = 8,
                              system_tags                    = system_tags,
                              status_variables               = status_variables,
                              timestamp_absolute_accuracy_ns = 0x3B9ACA00,
                              image_stream_config            = image_stream_config,
                              calibration_stream_config      = calibration_stream_config
                             )

status_variables_values = [
   1000000,
   1.0,
   2.5,
   512.0,
   1.0,
   600.0,
   'My Camera Id'
]
adv_writer.write(stream = SimpleAdv2Stream.IMAGE, data = b'\x10\x00\x10\x00', start_frame_clock_ticks = 1000, end_frame_clock_ticks = 2000, timestamp_middle_exposure_ns_since_2010 = 1000000, exposure_duration_ns = 10000, elapsed_time_clock_ticks = 2000, status_variables_values = status_variables_values)

#adv_writer.add_user_metadata_tag(name = 'my name', value = 'my value')

adv_writer.close()
