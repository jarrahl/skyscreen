"""
transform the polar coordinates into cartesian ones.
"""
import logging
import skyscreen_core
from skyscreen_core.interface import Screen
import numpy as np
import skyscreen_tools.flatspace_tools


n_screen_rows = Screen.screen_vane_count
n_screen_cols = Screen.screen_vane_count


class FlatSpaceTransform(skyscreen_core.interface.ScreenWriter):
	def __init__(self, writer):
		self.writer = writer
		self.screen_buffer = None

	def __enter__(self):
		assert self.screen_buffer is None, 'Cannot enter twice'
		self.writer_buf = self.writer.__enter__()
		self.writer_buf_resized = self.writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		self.screen_buffer = np.zeros((n_screen_rows, n_screen_cols, 3), dtype=np.uint8)
		return self.screen_buffer

	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self.writer, '__exit__'):
			self.writer.__exit__(exc_type, exc_val, exc_tb)

	def frame_ready(self):
		quickcopy_buffer(self.screen_buffer, self.writer_buf_resized)
		self.writer.frame_ready()


def quickcopy_buffer(input, output):
	skyscreen_tools.flatspace_tools.polar_remap(input, output)

def coord_mapping(mag, angle):
	return skyscreen_tools.flatspace_tools.polar_coord_transform(mag, angle)
