# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com

# this file includes classes of linear filters ready applied on the images
import numpy as np

from xinshuo_miscellaneous import isimsize

class linear_filter(object):
	def __init__(self, filter_size=None, warning=True, debug=True):
		'''
		generate a class of filter
		'''
		if debug: isimsize(filter_size), 'the filter size is not correct'
		self.debug = debug
		self.warning = warning
		self.filter_size = filter_size
		self.weights = None

	def gaussian_filter(self):
		'''
		generate Gaussian filter with a specific filter size
		'''
		if debug: assert filter_size is not None, 'the filter size is none'
		pass

	def sobel_filter(self, axis='x'):
		'''
		generate sobel filter along x or y axis
		'''
		if self.debug: assert axis in ['x', 'y'], 'the axis for sobel filter is not correct'

		if axis == 'x': sobel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype='float64')
		elif axis == 'y': sobel = np.array([[-1, -2, 1], [0, 0, 0], [1, 2, 1]], dtype='float64')
		self.weights = sobel

		return sobel