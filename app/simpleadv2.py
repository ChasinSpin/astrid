"""
Simple Astro Digital Video.

  - ADV Version 2 only
  - Native Python implementation (not dependent on C/C++ libraries)
  - Writer and Reader
  - Minimal implementation, reads what it write, may read what others write
  - Streamlined for writing raw frames directly from camera on cpu
    constrained systems
  - Example reader and write
"""

import os
import struct
from enum import Enum, auto


ADV2_REVISION = 2


class SimpleAdv2Stream(Enum):
    """Stream Enumeration."""

    IMAGE = 0
    CALIBRATION = 1


class SimpleAdv2Compression(Enum):
    """Compression Enumeration."""

    UNCOMPRESSED = auto()
    LAGARITH16 = auto()
    QUICKLZ = auto()


class SimpleAdv2DataLayout(Enum):
    """Data Layout Enumeration."""

    IMAGE_FULL_RAW = 'FULL-IMAGE-RAW'
    IMAGE_PACKED_12BIT = '12BIT-IMAGE-PACKED'
    IMAGE_COLOR_8BIT = '8BIT-COLOR-IMAGE'


class SimpleAdv2StatusDataType(Enum):
    """Status data type Enumeration."""

    INT8 = 0        # Signed 8 bit number (python type int)
    INT16 = 1	    # Signed 16 bit number (python type int)
    INT32 = 2       # Signed 32 bit number (python type int)
    INT64 = 3       # Signed 64 bit number (python type int)
    # A 32 bit floating point single precision number (IEEE 745)
    # (python type float)
    REAL = 4
    # A UTF8 string with a max length of 65535 chracaters (python type str)
    UTF8STRING = 5


class SimpleAdv2StreamConfig:
    """Object to hold stream configuration."""

    def __init__(self,
                 bits_per_pixel: int,
                 data_layout: SimpleAdv2DataLayout,
                 clock_frequency: int,
                 clock_accuracy: int,
                 compression: SimpleAdv2Compression,
                 regions_of_interest: list((int, int, int, int))):
        """Create SimpleAdvImageConfig.

        bits_per_pixel:  The number of bits per pixel for each image stored
        data_layout:     SimpleAdv2DataLayout (IMAGE_FULL_RAW, IMAGE_PACKED_12BIT
                         or IMAGE_COLOR_8BIT)
        clock_frequency: The frequency in Hz of the clock used to time the star
                         and end moment of the recorded data frames
        clock_accuracy:  Accuracy of the start and end timestamps in clock
                         ticks for the timings of data frames recorded
        compression:	 Compression method for the data see SimpleAdv2Compression
        regions_of_interest:
                         List of (left, top, width, height) tuples which define
                         regions of interest, or None
        """
        self.bits_per_pixel = bits_per_pixel
        self.clock_frequency = clock_frequency
        self.clock_accuracy = clock_accuracy
        self.compression = compression
        self.data_layout = data_layout
        self.regions_of_interest = regions_of_interest


class _UTF8String:

    def __init__(self, txt):
        self.string_as_bytes = bytes(txt, 'utf-8')
        self.length = 2 + len(self.string_as_bytes)

    def serialize(self):
        ser = struct.pack('<H', len(self.string_as_bytes))
        ser += self.string_as_bytes
        return ser


class _AdvHeader:
    def __init__(self):
        self._magic_value                       = 0x46545346    # 'FSTF'
        self._revision                          = ADV2_REVISION
        self._padding                           = 0
        self.offset_index_table                 = 0
        self.offset_system_metadata_table       = 0
        self.offset_user_metadata_table         = 0
        self.length                             = 4 + 1 + 4 + 8 + 8 + 8

    def serialize(self):
        ser = struct.pack('<IBIQQQ', \
                          self._magic_value,
                          self._revision,
                          self._padding,
                          self.offset_index_table,
                          self.offset_system_metadata_table,
                          self.offset_user_metadata_table,
                         )
        return ser


class _AdvDataStreamDefinition:

    def __init__(self,
                 name:str,
                 frequency:int,
                 timestamp_accuracy:int
                ):
        self._name                              = _UTF8String(name)
        self.number_of_dataframes               = 0
        self._frequency                         = frequency
        self._timestamp_accuracy                = timestamp_accuracy
        self.metadata_offset                    = 0   # There are no metadata entries, but we need to point to an offset later anyway
        self.length_header                      = self._name.length + 4 + 8 + 4 + 8
        self.length_metadata                    = 1

    def serialize_header(self):
        ser = self._name.serialize()
        ser += struct.pack('<IQIQ',
                           self.number_of_dataframes,
                           self._frequency,
                           self._timestamp_accuracy,
                           self.metadata_offset
                          )
        assert len(ser) == self.length_header, "serialized length != self.length"
        return ser

    def serialize_metadata(self):
        """Datastream metadata is always 0 in ADV2"""
        ser = b'\x00'
        assert len(ser) == self.length_metadata, "serialized length != self.length"
        return ser


class _AdvSectionDefinition:

    def __init__(self, name:str):
        self.name    = _UTF8String(name)
        self.offset = 0
        self.length  = self.name.length + 8

    def serialize(self):
        ser = self.name.serialize()
        ser += struct.pack('<Q', self.offset)
        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvDataStreamsDefinition:

    def __init__(self, header_length: int, image_stream_config: SimpleAdv2StreamConfig, calibration_stream_config: SimpleAdv2StreamConfig):
        self.datastreams = []
        self.length = 1    # Number of datastreams

        datastream = _AdvDataStreamDefinition('MAIN', image_stream_config.clock_frequency, calibration_stream_config.clock_accuracy)
        self.length += datastream.length_header
        self.datastreams.append(datastream)

        datastream = _AdvDataStreamDefinition('CALIBRATION', calibration_stream_config.clock_frequency, calibration_stream_config.clock_accuracy)
        self.length += datastream.length_header
        self.datastreams.append(datastream)

        self.sections = []
        self.length += 1   # Number of sections

        section = _AdvSectionDefinition('IMAGE')
        self.length += section.length
        self.sections.append(section)

        section = _AdvSectionDefinition('STATUS')
        self.length += section.length
        self.sections.append(section)

        # Update the metadata offsets for the datastreams
        for datastream in self.datastreams:
            datastream.metadata_offset = header_length + self.length
            self.length += datastream.length_metadata


    def serialize(self):
        ser = struct.pack('<B', len(self.datastreams))
        for datastream in self.datastreams:
             ser += datastream.serialize_header()

        ser += struct.pack('<B', len(self.sections))
        for section in self.sections:
            ser += section.serialize()

        for datastream in self.datastreams:
            ser += datastream.serialize_metadata()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvSectionImageLayout:

    def __init__(self, bits_per_pixel: int, tags: list((str, str))):
        self._revision       = ADV2_REVISION
        self._bits_per_pixel = bits_per_pixel
        self._tags           = []
        self.length          = 1 + 1 + 1

        for tag in tags:
            tag_new = (_UTF8String(tag[0]), _UTF8String(tag[1]))
            self._tags.append(tag_new)
            self.length += tag_new[0].length + tag_new[1].length

    def serialize(self):
        ser = struct.pack('<BBB', self._revision,
                          self._bits_per_pixel,
                          len(self._tags))
        for tag in self._tags:
            ser += tag[0].serialize() + tag[1].serialize()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser
 

class _AdvSectionImage:

    def _regions_of_interest_to_tags(rois: list((int, int, int, int))):
        tags = [('DATA-LAYOUT', 'IMAGE-ROIS'), ('ROI-COUNT', '%d'  % len(rois))]
        roi_id = 0
        for roi in rois:
            tags.append(('ROI-LEFT-%d' % roi_id, '%d' % roi[0]))
            tags.append(('ROI-TOP-%d' % roi_id, '%d' % roi[1]))
            tags.append(('ROI-WIDTH-%d' % roi_id, '%d' % roi[2]))
            tags.append(('ROI-HEIGHT-%d' % roi_id, '%d' % roi[3]))
            roi_id += 1

    def __init__(self,
                 dimensions: (int, int),
                 native_bits_per_pixel: int,
                 image_stream_config: SimpleAdv2StreamConfig,
                 calibration_stream_config: SimpleAdv2StreamConfig):
        self._revision              = ADV2_REVISION
        self._width                 = dimensions[0]
        self._height                = dimensions[1]
        self._native_bits_per_pixel = native_bits_per_pixel

        self._image_layouts         = []
        self.length = 1 + 4 + 4 + 1 + 1

        self._image_section_tags = []
        self.length += 1

        image_layout = _AdvSectionImageLayout(image_stream_config.bits_per_pixel,  [('DATA-LAYOUT', image_stream_config.data_layout.value),     ('SECTION-DATA-COMPRESSION', image_stream_config.compression.name)])
        self.length += image_layout.length + 1     # +1 for the id byte
        self._image_layouts.append(image_layout)

        image_layout = _AdvSectionImageLayout(calibration_stream_config.bits_per_pixel,  [('DATA-LAYOUT', calibration_stream_config.data_layout.value),     ('SECTION-DATA-COMPRESSION', calibration_stream_config.compression.name)])
        self.length += image_layout.length + 1     # +1 for the id byte
        self._image_layouts.append(image_layout)

        if image_stream_config.regions_of_interest is not None:
            tags = self._regions_of_interest_to_tags(image_stream_config.regions_of_interest)
            image_layout = _AdvSectionImageLayout(image_stream_config.bits_per_pixel, tags)
            self.length += image_layout.length + 1     # +1 for the id byte
            self._image_layouts.append(image_layout)

        if calibration_stream_config.regions_of_interest is not None:
            tags = self._regions_of_interest_to_tags(calibration_stream_config.regions_of_interest)
            image_layout = _AdvSectionImageLayout(calibration_stream_config.bits_per_pixel, tags)
            self.length += image_layout.length + 1     # +1 for the id byte
            self._image_layouts.append(image_layout)

        image_section_tag = (_UTF8String('IMAGE-BITPIX'), _UTF8String('%d' % self._native_bits_per_pixel))
        self._image_section_tags.append(image_section_tag)
        self.length += image_section_tag[0].length + image_section_tag[1].length

        image_section_tag = (_UTF8String('IMAGE-BYTE-ORDER'), _UTF8String('LITTLE-ENDIAN'))
        self._image_section_tags.append(image_section_tag)
        self.length += image_section_tag[0].length + image_section_tag[1].length

        #pymovie doesn't support color yet
        #image_section_tag = (_UTF8String('IMAGE-BAYER-PATTERN'), _UTF8String('BGGR'))
        #self._image_section_tags.append(image_section_tag)
        #self.length += image_section_tag[0].length + image_section_tag[1].length

    def serialize(self):
        ser = struct.pack('<BIIBB',
                          self._revision,
                          self._width,
                          self._height,
                          self._native_bits_per_pixel,
                          len(self._image_layouts))

        data_layout_id = 1
        for image_layout in self._image_layouts:
            ser += struct.pack('<B', data_layout_id)
            ser += image_layout.serialize()
            data_layout_id += 1

        ser += struct.pack('<B', len(self._image_section_tags))
        for tag in self._image_section_tags:
            ser += tag[0].serialize()
            ser += tag[1].serialize()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvSectionStatus:

    def __init__(self, timestamp_absolute_accuracy_ns: int, tags: list((str, int))):
        self._revision = ADV2_REVISION
        self._timestamp_absolute_accuracy_ns = timestamp_absolute_accuracy_ns
        self.length = 1 + 8 + 1

        self._tags = []
        for tag in tags:
            tag_new = (_UTF8String(tag[0]), tag[1])
            self.length += tag_new[0].length + 1
            self._tags.append(tag_new)

    def serialize(self):
        ser = struct.pack('<BQB',
                          self._revision,
                          self._timestamp_absolute_accuracy_ns,
                          len(self._tags)
                         )

        for tag in self._tags:
            ser += tag[0].serialize() 
            ser += struct.pack('<B', tag[1].value)

        assert len(ser) == self.length, "serialized length != self.length"
        return ser
          

class _AdvSystemMetadata:

    def __init__(self, tags: list((str, str))):
        self.length = 4

        self._tags = []
        for tag in tags:
            tag_new = (_UTF8String(tag[0]), _UTF8String(tag[1]))
            self.length += tag_new[0].length + tag_new[1].length
            self._tags.append(tag_new)

    def serialize(self):
        ser = struct.pack('<I', len(self._tags))

        for tag in self._tags:
            ser += tag[0].serialize() 
            ser += tag[1].serialize()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvPreamble:

    def __init__(self, dimensions: (int, int), native_bits_per_pixel: int, image_stream_config: SimpleAdv2StreamConfig, calibration_stream_config: SimpleAdv2StreamConfig, timestamp_absolute_accuracy_ns: int, status_variables: list((str, int)), system_tags: list((str,str))):
        self.advHeader = _AdvHeader()
        self.length = self.advHeader.length

        self.advDataStreamsDefinition = _AdvDataStreamsDefinition(self.advHeader.length, image_stream_config, calibration_stream_config)
        self.length += self.advDataStreamsDefinition.length

        # Fill in the IMAGE Section Offset now as it's after the data streams definition
        self.advDataStreamsDefinition.sections[0].offset = self.length

        self.advSectionImage = _AdvSectionImage(dimensions, native_bits_per_pixel, image_stream_config, calibration_stream_config)
        self.length += self.advSectionImage.length

        # Fill in the STATUS Section Offset now as it's after the IMAGE Section Offset
        self.advDataStreamsDefinition.sections[1].offset = self.length

        self.advSectionStatus = _AdvSectionStatus(timestamp_absolute_accuracy_ns, status_variables)
        self.length += self.advSectionStatus.length

        # Fill in the System Metadata Offset now as it's after the SectionData
        self.advHeader.offset_system_metadata_table = self.length

        self.advSystemMetadata = _AdvSystemMetadata(system_tags)
        self.length += self.advSystemMetadata.length

    def serialize(self):
        ser = self.advHeader.serialize()
        ser += self.advDataStreamsDefinition.serialize()
        ser += self.advSectionImage.serialize()
        ser += self.advSectionStatus.serialize()
        ser += self.advSystemMetadata.serialize()
        assert len(ser) == self.length, "serialized length != self.length"
        print('Preamble length: %d bytes' % self.length)
        return ser


class _AdvDataBlock:

    @classmethod
    def write_data(cls, file_handle, stream: SimpleAdv2Stream, data: bytes, start_frame_clock_ticks: int, end_frame_clock_ticks: int, timestamp_middle_exposure_ns_since_2010: int, exposure_duration_ns: int, status_variables: list((str, int)), status_variables_values: list):
        block_header = struct.pack('<IBQQIBB',
                                   0xEE0122FF,
                                   stream.value,
                                   start_frame_clock_ticks,
                                   end_frame_clock_ticks,
                                   1 + 1 + len(data),
                                   stream.value + 1,
                                   0)
        file_handle.write(block_header)
        file_handle.write(data)

        status_header_length = 4 + 8 + 4 + 1
        assert len(status_variables) == len(status_variables_values), "status_variables and status_variables_values must have the same number"

        packed_status_vars = b''
        for i in range(len(status_variables)):
            print(status_variables[i])
            if   status_variables[i][1] == SimpleAdv2StatusDataType.INT8:
                packed_status_vars += struct.pack('<b', status_variables_values[i])

            elif status_variables[i][1] == SimpleAdv2StatusDataType.INT16:
                packed_status_vars += struct.pack('<h', status_variables_values[i])

            elif status_variables[i][1] == SimpleAdv2StatusDataType.INT32:
                packed_status_vars += struct.pack('<i', status_variables_values[i])

            elif status_variables[i][1] == SimpleAdv2StatusDataType.INT64:
                packed_status_vars += struct.pack('<q', status_variables_values[i])

            elif status_variables[i][1] == SimpleAdv2StatusDataType.REAL:
                packed_status_vars += struct.pack('<f', status_variables_values[i])

            elif status_variables[i][1] == SimpleAdv2StatusDataType.UTF8STRING:
                packed_status_vars += _UTF8String(status_variables_values[i]).serialize()

            else:
                raise ValueError("Invalid SimpleAdv2StatusDataType")

        status_header_length += len(packed_status_vars)

        status_header = struct.pack('<IQIB',
                                    status_header_length - 4, 	# Starts at the next field
                                    timestamp_middle_exposure_ns_since_2010,
                                    exposure_duration_ns,
                                    len(status_variables_values))
        status_header += packed_status_vars

        file_handle.write(status_header)



class _AdvIndexTableBlockIndexEntry:
    def __init__(self, elapsed_time_clock_ticks: int, offset_data_frame: int, data_frame_length: int):
        """
            elapsed_time_clock_ticks: Elapased time in data stream clock ticks since the first frame in the data
            offset_data_rame: The offset of the data frame from the beginning of the file.
            data_frame_length:  The length of the data frame in bytes excluding the data frame MAGIC id.
        """
        self._elapsed_time_clock_ticks = elapsed_time_clock_ticks
        self._offset_data_frame = offset_data_frame
        self._data_frame_length = data_frame_length
        self.length = 8 + 8 + 4

    def serialize(self):
        ser = struct.pack('<QQI', self._elapsed_time_clock_ticks, self._offset_data_frame, self._data_frame_length)
        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvIndexTableBlock:

    def __init__(self):
        self._index_entries = []
        self.length = 4

    def add_index_entry(self, elapsed_time_clock_ticks: int, offset_data_frame: int, data_frame_length: int):
        index_table_block_index_entry = _AdvIndexTableBlockIndexEntry(elapsed_time_clock_ticks, offset_data_frame, data_frame_length)
        self._index_entries.append(index_table_block_index_entry)
        self.length += index_table_block_index_entry.length

    def serialize(self):
        ser = struct.pack('<I', len(self._index_entries))
        for index_entry in self._index_entries:
            ser += index_entry.serialize()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class _AdvIndexTable:

    def __init__(self):
        self._index_block_main = _AdvIndexTableBlock()               # MAIN
        self._index_block_calibration = _AdvIndexTableBlock()        # CALIBRATION
        self.length = 0

    def add_index_entry(self, stream: SimpleAdv2Stream, elapsed_time_clock_ticks: int, offset_data_frame: int, data_frame_length: int):
        if   stream == SimpleAdv2Stream.IMAGE:
            self._index_block_main.add_index_entry(elapsed_time_clock_ticks, offset_data_frame, data_frame_length)
        elif stream == SimpleAdv2Stream.CALIBRATION:
            self._index_block_calibration.add_index_entry(elapsed_time_clock_ticks, offset_data_frame, data_frame_length)

    def serialize(self):
        self.length = 1 + 4 + 4

        self._offset_main = self.length
        self._offset_calibration = self._offset_main +  self._index_block_main.length
        self.length += self._index_block_main.length
        self.length += self._index_block_calibration.length

        ser = struct.pack('<BII', 2, self._offset_main, self._offset_calibration)
        ser += self._index_block_main.serialize()
        ser += self._index_block_calibration.serialize()

        assert len(ser) == self.length, "serialized length != self.length"
        return ser


class SimpleAdv2Writer:
    """Write Astro Digital Video."""

    def __write_preamble(self):
        """Write preample (Header Data, Streams Definition, Metadata, System 
        Metadata to file. This may have to be written more than once as information
        is updated like offsets, frame counts etc.
        """ 

        # Seek to beginning of file and write the preamble
        self.file_handle.seek(0, 0)
        self.file_handle.write(self._advPreamble.serialize())

        self._need_seek_end = True

    def __init__(self,
                 file_handle,
                 dimensions: (int, int),
                 native_bits_per_pixel: int,
                 system_tags: list((str, str)),
                 status_variables: list((str, int)),
                 timestamp_absolute_accuracy_ns: int,
                 image_stream_config: SimpleAdv2StreamConfig,
                 calibration_stream_config: SimpleAdv2StreamConfig):
        """Create SimpleAdv2Writer.

        file_handle:               open file haneld
        dimensions:                (width, height) dimensions of the image
        native_bits_per_pixel:     Native bits per pixel of the data
                                   acquired from the camer. This may
                                   be different from the BPP of individual
                                   images. Camera may return images in
                                   16 bit format, but the values in the pixels
                                   may be 12 bit with a maximum value of 4095.
        system_tags:               list of (name, value) tuples
        status_variables:          list of (name, type) tuples
        image_stream_config:       SimpleAdv2StreamConfig for image stream
        calibration_stream_config: SimpleAdv2StreamConfig for calibration
                                   stream

        Raises:
            standard file errors, including if file already exists 
        """
        self._need_seek_end = False
        #self.filename = filename
        self.dimensions = dimensions
        self.native_bits_per_pixel = native_bits_per_pixel
        self.system_tags = system_tags
        self.status_variables = status_variables
        self.image_stream_config = image_stream_config
        self.calibration_stream_config = calibration_stream_config
        self._user_metadata_tags = []  # List of (name, value)

        # Open file, check if exists first, because we don't want to overwirte
        #if os.path.exists(self.filename):
        #    raise FileExistsError(self.filename)

        #self.file_handle = open(self.filename, 'wb')
        self.file_handle = file_handle

        self._advPreamble = _AdvPreamble(self.dimensions, self.native_bits_per_pixel, self.image_stream_config, self.calibration_stream_config, timestamp_absolute_accuracy_ns, status_variables, system_tags)
        self.__write_preamble()

        self._index_table = _AdvIndexTable()


    def write(self, stream: SimpleAdv2Stream, data: bytes, start_frame_clock_ticks: int, end_frame_clock_ticks: int, timestamp_middle_exposure_ns_since_2010: int, exposure_duration_ns: int, elapsed_time_clock_ticks: int, status_variables_values: list):
        """Write data and status_variables_values to stream.

        stream:                  SimpleAdv2Stream stream to write to
        data:                    Image data to write in bytes
        status_variables_values: The values in the same order/quantity
                                 defined in status_variables when
                                 creating the object.
        """
        if self._need_seek_end:
            self._need_seek_end = False
            self.file_handle.seek(0, 2)

        offset_data_frame = self.file_handle.tell()

        _AdvDataBlock.write_data(self.file_handle, stream, data, start_frame_clock_ticks, end_frame_clock_ticks, timestamp_middle_exposure_ns_since_2010, exposure_duration_ns,self.status_variables, status_variables_values)
        self._advPreamble.advDataStreamsDefinition.datastreams[stream.value].number_of_dataframes += 1

        data_frame_length = (self.file_handle.tell() - offset_data_frame) - 4

        self._index_table.add_index_entry(stream, elapsed_time_clock_ticks, offset_data_frame, data_frame_length)

    def add_user_metadata_tag(self, name: str, value: str):
        """Add a user metadata tag to the end of the file.

        This is added, but only written on close.
        If an existing user data tag exists, it's overwritten.
        """
        # Overwrite tag with new value in place if it exists
        for i in range(len(self._user_metadata_tags)):
            tag = self._user_metadata_tags[i]
            if tag[0] == name:
                self._user_metadata_tags[i] = (tag[0], value)
                return

        # Add new tag
        self._user_metadata_tags.append((name, value))

    def close(self):
        """
        Close the ADC file.

        Updates the header, offsets, frame counts and writes the Index Table
        and User Metadata Table.
        """

        if self._need_seek_end:
            self._need_seek_end = False
            self.file_handle.seek(0, 2)

        self._advPreamble.advHeader.offset_index_table = self.file_handle.tell()
        self.file_handle.write(self._index_table.serialize())

        self._advPreamble.advHeader.offset_user_metadata_table = self.file_handle.tell()
        ser = struct.pack('<I', len(self._user_metadata_tags))
        for tag in self._user_metadata_tags:
            ser += _UTF8String(tag[0]).serialize() + _UTF8String(tag[1]).serialize()   
        self.file_handle.write(ser)

        # Write preamble to update the offset_index_table and offset_user_metadata_table
        self.__write_preamble()

        #self.file_handle.close()


class SimpleAdv2Reader:
    """Good comment."""

    def __init__(self):
        """Good comment2."""
        self.test = True
        if self.test is not None:
            print('hello')

    def test_hello(self):
        """A good method."""
        print('hello')
        return self.test

    # Weird comment
    def test_hello2(self):
        """Doc string2."""
        print('hello2', self.test)
