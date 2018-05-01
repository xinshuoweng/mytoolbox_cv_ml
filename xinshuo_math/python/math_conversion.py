# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com

# this file includes basic functions to convert the format of numpy array for further computation
import cv2, numpy as np

from private import safe_2dptsarray_occlusion, safe_npdata
from xinshuo_miscellaneous import isscalar, isimsize, isnparray

############################################# format conversion #################################
def nparray_hwc2chw(input_nparray, warning=True, debug=True):
	'''
	this function transpose the channels of an numpy array from HWC to CHW

	parameters:
	    input_nparray:  a numpy HWC array

	outputs:
	    np_array:       a numpy CHW array
	'''
	np_array = safe_npdata(input_nparray, warning=warning, debug=debug)
	if debug: assert np_array.ndim == 3, 'the input numpy array does not have a good dimension: {}'.format(np_image.shape)

	return np.transpose(np_array, (2, 0, 1)) 

def nparray_chw2hwc(input_nparray, warning=True, debug=True):
	'''
	this function transpose the channels of an numpy array  from CHW to HWC

	parameters:
	    input_nparray:  a numpy CHW array

	outputs:
	    np_array:       a numpy HWC array
	'''
	if debug: isnparray(input_nparray), 'the input array is not a numpy'
	np_array = input_nparray.copy()
	if debug: assert np_array.ndim == 3, 'the input numpy array does not have a good dimension: {}'.format(np_image.shape)

	return np.transpose(np_array, (1, 2, 0)) 

def generate_gaussian_heatmap(input_pts, image_size, std, warning=True, debug=True):
	'''
	generate a heatmap based on the input points array, create a 2-D gaussian with given std around each points provided
	the mask is generated by the occlusion from the point array: only occlusion with -1 will be masked out
	    0 -> invisible points without location
	    1 -> visible points with location
	    -1 -> visible points without location, masked

	parameters:
	    input_pts:          a list of 3 elements, a listoflist of 3 elements: e.g., [[1,2], [5,6], [0, 1]],
	                        a numpy array with shape or (3, N) or (3, )
	    image_size:         a tuple or list of numpy array with 2 elements, representing (height, width)
	    std:                the standard deviation used for gaussian distribution

	outputs:
	    masked_heatmap:         numpy float32 multichannel numpy array, (height, width, num_pts + 1)
	    mask_valid:             numpy float32 multichannel numpy array, (1, 1, num_pts + 1)
	    mask_visible:           numpy float32 multichannel numpy array, (1, 1, num_pts + 1)
	'''
	pts_array = safe_2dptsarray_occlusion(input_pts, warning=warning, debug=debug)
	if debug:
		assert isscalar(std), 'the standard deviation should be a scalar'
		assert isimsize(image_size), 'the image size is not correct'
	height, width = image_size[0], image_size[1]
	num_pts, threshold = pts_array.shape[1], 0.01
	heatmap = np.fromfunction( lambda y, x, pts_id : ((x - pts_array[0, pts_id])**2 \
	                                                + (y - pts_array[1, pts_id])**2) \
	                                                / -2.0 / std / std, (height, width, num_pts), dtype=int)
	heatmap = np.exp(heatmap)

	valid = np.logical_or(pts_array[2, :] == 0, pts_array[2, :] == 1)       # mask out invalid points with -1 in the third
	visible = pts_array[2, :] == 1                                          # mask out invalid and occuluded points
	mask_valid = np.ones((1, 1, num_pts+1), dtype='float32')
	mask_valid[0, 0, :num_pts] = valid                                      # never mask out the background channel
	mask_visible = np.ones((1, 1, num_pts+1), dtype='float32')
	mask_visible[0, 0, :num_pts] = visible                                  # never mask out the background channel

	# mask out the invalid channel
	heatmap[heatmap < threshold] = 0                                    # ceiling and flooring
	heatmap[heatmap >         1] = 1
	masked_heatmap = heatmap * mask_valid[:, :, :num_pts]               # (height, width, num_pts)

	background_label = 1 - np.amax(masked_heatmap, axis=2)              # (height, width), maximize along the channel axis
	background_label[background_label < 0] = 0                          # (height, width, 1)
	masked_heatmap = np.concatenate((masked_heatmap, np.expand_dims(background_label, axis=2)), axis=2).astype('float32')

	return masked_heatmap, mask_valid, mask_visible

############################################# 2D transformation #################################
def nparray_resize(input_nparray, resize_factor=None, target_size=None, interp='bicubic', warning=True, debug=True):
    '''
    resize the numpy array given a resize factor (e.g., 0.25), or given a target size (height, width)
    e.g., the numpy array has 600 x 800:
        1. given a resize factor of 0.25 -> results in an image with 150 x 200
        2. given a target size of (300, 400) -> results in an image with 300 x 400
    note that:
        resize_factor and target_size cannot exist at the same time

    parameters:
        input_nparray:      a numpy array
        resize_factor:      a scalar
        target_size:        a list of tuple or numpy array with 2 elements, representing height and width
        interp:             interpolation methods: bicubic or bilinear

    outputs:
        resized_nparray:    a numpy array
    ''' 
    np_array = safe_npdata(input_nparray, warning=warning, debug=debug)
    if debug:
        assert interp in ['bicubic', 'bilinear'], 'the interpolation method is not correct'
        assert (resize_factor is not None and target_size is None) or (resize_factor is None and target_size is not None), 'resize_factor and target_size cannot co-exist'

    if target_size is not None:
        if debug: assert isimsize(target_size), 'the input target size is not correct'
        target_width, target_height = int(round(target_size[1])), int(round(target_size[0]))
    elif resize_factor is not None:
        if debug: assert isscalar(resize_factor), 'the resize factor is not a scalar'
        height, width = np_array.shape[:2]
        target_width, target_height = int(round(resize_factor * width)), int(round(resize_factor * height))
    else: assert False, 'the target_size and resize_factor do not exist'

    if interp == 'bicubic':
        resized_nparray = cv2.resize(np_array, (target_width, target_height), interpolation = cv2.INTER_CUBIC)
    elif interp == 'bilinear':
        resized_nparray = cv2.resize(np_array, (target_width, target_height), interpolation = cv2.INTER_LINEAR)
    else: assert False, 'interpolation is wrong'

    return resized_nparray