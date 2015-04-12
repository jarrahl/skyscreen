import logging
import os
import random
import sys
import argparse
import time

import numpy as np

from skyscreen_core.interface import Screen, pixel_vane_mapping
import skyscreen_core.memmap_interface
import skyscreen_core.mmap_interface

def bands(writer, lock):
	r = (255, 0, 0)
	g = (0, 255, 0)
	b = (0, 0, 255)
	band_matrix = np.zeros(shape=(Screen.screen_vane_count, Screen.screen_vane_length, 3))

	count = 0

	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		lock.frame_ready()
		while True:
			for band in xrange(Screen.screen_vane_count):
				band_matrix[band, :, 0] = 255 * (band % 3 == ((count + 0) % 3))
				band_matrix[band, :, 1] = 255 * (band % 3 == ((count + 1) % 3))
				band_matrix[band, :, 2] = 255 * (band % 3 == ((count + 2) % 3))
				writer_buf_reshaped[:] = band_matrix
			count += 1
			print '.',; sys.stdout.flush()

