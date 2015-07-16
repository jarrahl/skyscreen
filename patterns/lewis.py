import numpy as np
import colorsys
import random

from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("lewis")
class LewisCarrollCLI(cli.Application, PatternPlayerMixin):
	"""
	Named after Lewis Carroll, for being:
	a) mathematical
	b) beautiful in its elegance
	c) psychedelic and trippy as SHIT
	"""
	def main(self):
		self.main_from_renderer(lewis_carroll)


def lewis_carroll(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""

	with writer as writer_buf:
		count = Screen.screen_max_magnitude
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		N = 5
		while True:
			if count % 30 == 0:
				N += 1

			buf = screen[0:2, :, :]
			screen[:-2, :, :] = screen[2:, :, :]
			screen[-2:, :, :] = buf
			screen[:, 2:, :] = screen[:,:-2,:]
			for i in xrange(Screen.screen_vane_count/2):
				x = (2*i - count + Screen.screen_vane_count) % Screen.screen_vane_count
				screen[x:x+2, 0:2, :] = np.array(colorsys.hsv_to_rgb((((i+1)*(count)) % N) / float(N), 1, 1)) * 255
			writer_buf_reshaped[:,:,:] = screen
			writer.frame_ready()
			count += 1

