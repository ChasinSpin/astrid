#!//usr/bin/env python3

import sys
import cv2
import numpy as np
from ravf import RavfReader, RavfImageUtils, RavfImageFormat


if len(sys.argv) != 3:
    print('Usage: %s lower upper' % sys.argv[0])
    sys.exit(-1)

lower = int(sys.argv[1])
upper = int(sys.argv[2])


file_handle = open('movie.ravf', 'rb')

ravf = RavfReader(file_handle = file_handle)
print('RAVF Version:', ravf.version())
print('Metadata:', ravf.metadata())
print('Timestamps:', ravf.timestamps())
print('Frame Count:', ravf.frame_count())

stride = ravf.metadata_value('IMAGE-ROW-STRIDE')
height = ravf.metadata_value('IMAGE-HEIGHT')
width = ravf.metadata_value('IMAGE-WIDTH')
format = ravf.metadata_value('IMAGE-FORMAT')

grayscale = True

for i in range(ravf.frame_count()):
    frame = ravf.frame_by_index(file_handle, i)


    if ravf.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_PACKED_10BIT.value:
        image = RavfImageUtils.bytes_to_np_array(frame.data, stride, height)
        image = RavfImageUtils.unstride_10bit(image, width, height)
        image = RavfImageUtils.unpack_10bit_pigsc(image, width, height, stride)
        image = RavfImageUtils.scale_10_to_16bit(image)
        #if grayscale:
        #    image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        #else:
        #    image = RavfImageUtils.debayer_BGGR_to_BGR(image)
    elif ravf.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_PACKED_12BIT.value:
        image = RavfImageUtils.bytes_to_np_array(frame.data, stride, height)
        image = RavfImageUtils.unstride_12bit(image, width, height)
        image = RavfImageUtils.unpack_12bit_pihq(image, width, height, stride)
        image = RavfImageUtils.scale_12_to_16bit(image)
        if grayscale:
            image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        else:
            image = RavfImageUtils.debayer_BGGR_to_BGR(image)
    elif ravf.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_UNPACKED_12BIT.value:
        print("Unpacked 12")
        image = RavfImageUtils.bytes_to_np_array_16bit(frame.data, stride, height)
        image = RavfImageUtils.unstride_16bit(image, width, height)
        image = RavfImageUtils.scale_12_to_16bit(image)
        if grayscale:
            image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        else:
            image = RavfImageUtils.debayer_BGGR_to_BGR(image)
    elif ravf.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_UNPACKED_10BIT.value:
        print("Unpacked 10")
        image = RavfImageUtils.bytes_to_np_array_16bit(frame.data, stride, height)
        image = RavfImageUtils.unstride_16bit(image, width, height)
        image = RavfImageUtils.scale_10_to_16bit(image)
        if grayscale:
            image = RavfImageUtils.debayer_GBRG_to_GRAY(image)
        else:
            image = RavfImageUtils.debayer_GBRG_to_BGR(image)
    else:
        raise ValueError('Unrecognized image type')

    print(image.shape)
    print('Max:', np.max(image))
    print('Min:', np.min(image))

    print(image)
    image = image - lower
    print(image)
    mult = 65535 / (upper - lower)
    print(mult)
    image = image.astype(np.float32)
    print(image)
    image = image * mult
    image = np.clip(image, 0.0, 65535.0)
    print(image)
    image = image.astype(np.uint16)
    print(image)

    #image[:,:,0] = image[:,:,0] * 1.5 * 1.5
    #image[:,:,1] = image[:,:,1] * 0.7 * 1.5
    #image[:,:,2] = image[:,:,2] * 1.3 * 1.5
 
    if width == 4096:
        cv2.imshow('bgr', cv2.resize(image, (width//4, height//4)))
    else:
        cv2.imshow('bgr', image)

    key = cv2.waitKey()
    print(key)
    if key == 113:    # q
       break

file_handle.close()

cv2.destroyAllWindows()
