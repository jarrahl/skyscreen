"""
transform the polar coordinates into cartesian ones.
"""
import cv2
import math
import skyscreen_core
from skyscreen_core.interface import Screen
import numpy as np
import skyscreen_tools.flatspace_tools
import skyscreen_core.interface as interface

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
	mags = np.round(Screen.screen_max_magnitude - mags).astype(np.int32) + annulus
	return mags, angles

mags, angles = make_mapping_matrix(None)

class FlatSpaceTransform(skyscreen_core.interface.ScreenWriter):
	def __init__(self, writer):
		self.writer = writer
		self.screen_buffer = None
		self.blurred_buffer = None

	def __enter__(self):
		assert self.screen_buffer is None, 'Cannot enter twice'
		self.writer_buf = self.writer.__enter__()
		self.writer_buf_resized = self.writer_buf.reshape((Screen.screen_rows, Screen.screen_cols, 3))
		self.screen_buffer = np.zeros((paintable_area, paintable_area, 3), dtype=np.uint8)
		self.blurred_buffer = np.zeros((paintable_area, paintable_area, 3), dtype=np.uint8)
		return self.screen_buffer

	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self.writer, '__exit__'):
			self.writer.__exit__(exc_type, exc_val, exc_tb)

	def frame_ready(self):
		blurred_buffer = np.zeros((Screen.screen_rows, Screen.screen_cols, 3), dtype=np.uint8)
		quickcopy_buffer(self.screen_buffer, self.writer_buf_resized)
		self.writer.frame_ready()

def quickcopy_buffer(input, output):
	skyscreen_tools.flatspace_tools.blit(input, output, mags, angles)
