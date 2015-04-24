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
	band_matrix = np.zeros(shape=(Screen.screen_vane_count, Screen.screen_vane_length, 3))

	count = 0

	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		while True:
			lock.frame_ready()
			for angle in xrange(Screen.screen_vane_count):
				band_matrix[angle, :, 0] = 255 * (angle % 3 == ((count + 0) % 3))
				band_matrix[angle, :, 1] = 255 * (angle % 3 == ((count + 1) % 3))
				band_matrix[angle, :, 2] = 255 * (angle % 3 == ((count + 2) % 3))
				writer_buf_reshaped[:] = band_matrix
			count += 1
			print '.',; sys.stdout.flush()

