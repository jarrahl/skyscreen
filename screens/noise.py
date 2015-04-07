import random
import sys

import numpy as np

from skyscreen_core.interface import Screen, pixel_vane_mapping


def numpy_random(writer):
	with writer as writer_buf:
		while True:
			writer_buf[:] = 255*np.random.random(size=writer_buf.shape)
			writer_buf.flush()

def noise(writer):
	with writer as writer_buf:
		while True:
			print '.',; sys.stdout.flush()
			for vane in xrange(Screen.screen_vane_count):
				for pixel in xrange(Screen.screen_vane_length):
					for channel in {'r', 'g', 'b'}:
						c = random.randint(0, 255)
						offset = pixel_vane_mapping(vane, pixel, channel)
						writer_buf[offset] = c
