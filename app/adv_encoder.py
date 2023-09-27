""" ADV encoder functionality """

from simpleadv2 import SimpleAdv2Writer, SimpleAdv2StreamConfig, SimpleAdv2Stream, SimpleAdv2Compression, SimpleAdv2StatusDataType, SimpleAdv2DataLayout

from picamera2.encoders.encoder import Encoder

class AdvEncoder(Encoder):

    def __init__(self, bits_per_pixel: int,
                       native_bits_per_pixel: int,
                       data_layout: SimpleAdv2DataLayout,
                       clock_frequency: int, 
                       clock_accuracy: int,
                       timestamp_absolute_accuracy_ns: int,
                       compression: SimpleAdv2Compression,
                       regions_of_interest: list((int, int, int, int))
                ):
        super().__init__()
        self._adv_writer = None
        self._image_stream_config = None
        self._calibraion_stream_config = None
        self._system_tags = None
        self._status_variables = None
        self._bits_per_pixel = bits_per_pixel
        self._native_bits_per_pixel = native_bits_per_pixel
        self._data_layout = data_layout
        self._clock_frequency = clock_frequency
        self._clock_accuracy = clock_accuracy
        self._timestamp_absolute_accuracy_ns = timestamp_absolute_accuracy_ns
        self._compression = compression
        self._regions_of_interest = regions_of_interest

        self._system_tags = [
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
            ('BITPIX', '%d' % self._bits_per_pixel),
            ('FSTF-TYPE', 'ADV'),
            ('WIDTH', '4064'),
            ('HEIGHT', '%d' % self.height),
        ]

        self._status_variables = [
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

        print('Width:', self.width)
        print('Height:', self.height)


    def start(self):
        super().start()

        self._image_stream_config       = SimpleAdv2StreamConfig(self._bits_per_pixel, self._data_layout, self._clock_frequency, self._clock_accuracy, self._compression, self._regions_of_interest)
        self._calibration_stream_config = SimpleAdv2StreamConfig(self._bits_per_pixel, self._data_layout, self._clock_frequency, self._clock_accuracy, self._compression, self._regions_of_interest)

        # start opens the file 
        self._advwriter = SimpleAdv2Writer(file_handle                    = self.output.fileoutput,
                                           dimensions                     = (4064, self.height),
                                           native_bits_per_pixel          = self._native_bits_per_pixel,
                                           system_tags                    = self._system_tags,
                                           status_variables               = self._status_variables,
                                           timestamp_absolute_accuracy_ns = self._timestamp_absolute_accuracy_ns,
                                           image_stream_config            = self._image_stream_config,
                                           calibration_stream_config      = self._calibration_stream_config
                                          )

    def stop(self):
        # self._advwriter.add_user_metadata_tag(name = 'my name', value = 'my value')
        self._advwriter.close()

        # stop closes the file
        super().stop()

    def outputframe(self, frame, keyframe=True, timestamp=None):
        status_variables_values = [
            float(1.0),
            float(1.5),
            float(512.0),
            int(1000),
            int(1),
            int(1),
            int(8),
            int(3),
            int(3),
            int(3),
            'No Errors'
        ]

        if self.output.recording:
            print('Frame length:', len(frame))
            self._advwriter.write(stream = SimpleAdv2Stream.IMAGE, data = frame, start_frame_clock_ticks = 1000, end_frame_clock_ticks = 2000, timestamp_middle_exposure_ns_since_2010 = 1000000, exposure_duration_ns = 10000, elapsed_time_clock_ticks = 2000, status_variables_values = status_variables_values)
