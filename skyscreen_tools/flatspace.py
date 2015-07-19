"""
transform the polar coordinates into cartesian ones.
"""
import logging
import cv2
import skyscreen_core
from skyscreen_core.interface import Screen
import skyscreen_core.interface as interface

# These are for when you use cython
# import pyximport; pyximport.install()
# import skyscreen_tools.flatspace_tools

import numpy as np
import ctypes

logging.warning("Loading C tools")
# Pull in the libflatspace_faster library
_blittools = np.ctypeslib.load_library('libflatspace_faster', './skyscreen_tools/')
# The blit function takes the input and output arrays
_blittools.blit_polar.restype = None
_blittools.blit_polar.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8)]
# The initalize_globals function lets you set the globals in the c program
_blittools.initialize_globals.restype = None
_blittools.initialize_globals.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
logging.warning("C tools loaded")

n_screen_rows = Screen.screen_vane_count
n_screen_cols = Screen.screen_vane_count

output_location = None
window_size = 800
annulus = 50
paintable_area = interface.Screen.screen_max_magnitude*2+annulus*2

def make_mapping_matrix(v):
	rows = np.zeros((paintable_area, paintable_area))
	cols = np.zeros((paintable_area, paintable_area))

	for row in xrange(paintable_area):
		for col in xrange(paintable_area):
			rows[row, col] = (row - paintable_area/2) / 0.9
			cols[row, col] = (col - paintable_area/2) / 0.9
	mags, angles = cv2.cartToPolar(cols, rows)
	angles = np.round((angles / (2 * 3.141592) * 360)).astype(np.int32)
	mags = (np.round(Screen.screen_max_magnitude - mags) + annulus).astype(np.int32)
	return mags, angles

mags, angles = make_mapping_matrix(None)
assert mags.shape == (paintable_area, paintable_area), ("mags has shape: %s" % str(mags.shape))
assert angles.shape == (paintable_area, paintable_area), ("angles has shape: %s" % str(mags.shape))
mags_cdata = mags.ctypes.data_as(ctypes.POINTER(ctypes.c_uint))
angles_cdata = angles.ctypes.data_as(ctypes.POINTER(ctypes.c_uint))
_blittools.initialize_globals(mags_cdata, angles_cdata)

class FlatSpaceTransform(skyscreen_core.interface.ScreenWriter):
	def __init__(self, writer):
		self.writer = writer
		self.screen_buffer = None

	def __enter__(self):
		assert self.screen_buffer is None, 'Cannot enter twice'
		self.writer_buf = self.writer.__enter__()
		self.writer_buf_resized = self.writer_buf.reshape((Screen.screen_rows, Screen.screen_cols, 3))
		self.screen_buffer = np.zeros((paintable_area, paintable_area, 3), dtype=np.uint8)
		self.screen_buffer_ptr = self.screen_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
		self.writer_buf_resized_ptr = self.writer_buf_resized.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
		return self.screen_buffer

	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self.writer, '__exit__'):
			self.writer.__exit__(exc_type, exc_val, exc_tb)

	def frame_ready(self):
		_blittools.blit_polar(self.screen_buffer_ptr, self.writer_buf_resized_ptr)
		self.writer.frame_ready()

