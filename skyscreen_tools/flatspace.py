"""
transform the polar coordinates into cartesian ones.
"""
import logging
from skyscreen_core.interface import Screen
import numpy as np
import pyximport; pyximport.install()
import skyscreen_tools.flatspace_tools


n_screen_rows = Screen.screen_vane_length
n_screen_cols = Screen.screen_vane_length

screen_row_coords = np.linspace(0, n_screen_rows-1, n_screen_rows) - (n_screen_rows / 2)
x = np.resize(screen_row_coords, (n_screen_rows, n_screen_cols))
y = -np.resize(screen_row_coords, (n_screen_rows, n_screen_cols)).T

angle = np.round(np.sin(y/x) / (2*np.pi) * Screen.screen_vane_count)
mag = np.sqrt(np.power(x, 2), np.power(y, 2))

class FlatSpaceTransform(object):
	def __init__(self, writer, lock):
		self.lock = lock
		self.writer = writer
		self.screen_buffer = None

	def __enter__(self):
		assert self.screen_buffer is None, 'Cannot enter twice'
		self.writer_buf = self.writer.__enter__()
		self.writer_buf_resized = self.writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		self.screen_buffer = np.zeros((n_screen_rows, n_screen_cols, 3))
		return self.screen_buffer

	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self.writer, '__exit__'):
			self.writer.__exit__(exc_type, exc_val, exc_tb)

	def frame_ready(self):
		logging.warning('Copying frame contents')
		quickcopy_buffer(self.writer_buf_resized, self.screen_buffer)
		self.lock.frame_ready()


def quickcopy_buffer(input, output):
	skyscreen_tools.flatspace_tools.polar_remap(input, output)
