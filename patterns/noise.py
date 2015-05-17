import random
import sys

import numpy as np
from plumbum import cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

from skyscreen_core.interface import Screen, pixel_vane_mapping


@PatternPlayer.subcommand("noise")
class NoisePattern(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(noise)


@PatternPlayer.subcommand("npnoise")
class NPNoisePattern(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(numpy_random)

def numpy_random(writer):
	with writer as writer_buf:
		while True:
			writer.frame_ready()
			writer_buf[:] = 255*np.random.random(size=writer_buf.shape)
			writer_buf.flush()

def noise(writer):
	with writer as writer_buf:
		while True:
			writer.frame_ready()
			print '.',; sys.stdout.flush()
			for vane in xrange(Screen.screen_vane_count):
				for pixel in xrange(Screen.screen_max_magnitude):
					for channel in {'r', 'g', 'b'}:
						c = random.randint(0, 255)
						offset = pixel_vane_mapping(vane, pixel, channel)
						writer_buf[offset] = c
