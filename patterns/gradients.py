import numpy as np
from functools import partial
import colorsys
import random
import math
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
from skyscreen_core.interface import Screen
import noise

@PatternPlayer.subcommand("gradients-perlin")
class GradientsPerlinMedCLI(cli.Application, PatternPlayerMixin):
	"""
	Create smooth colour gradient with Perlin noise.
	"""
	def main(self):
		self.main_from_renderer(partial(gradients_perlin, period = 300.0, speed = 5))

@PatternPlayer.subcommand("gradients-smooth")
class GradientsPerlinCLI(cli.Application, PatternPlayerMixin):
	"""
	Create smooth colour gradient with Perlin noise.
	"""
	def main(self, period, speed):
		self.main_from_renderer(partial(gradients_perlin, period = period, speed = speed))

@PatternPlayer.subcommand("gradients-slow")
class GradientsSlowCLI(cli.Application, PatternPlayerMixin):
	"""
	Create linear gradients with period 100, speed 2.
	"""
	def main(self):
		self.main_from_renderer(partial(gradients, period = 100, speed = 2))

@PatternPlayer.subcommand("gradients-med")
class GradientsMedCLI(cli.Application, PatternPlayerMixin):
	"""
	Create linear gradients with period 60, speed 3.
	"""
	def main(self):
		self.main_from_renderer(partial(gradients, period = 60, speed = 3))

@PatternPlayer.subcommand("gradients-fast")
class GradientsFastCLI(cli.Application, PatternPlayerMixin):
	"""
	Create linear gradients with period 30, speed 5.
	"""
	def main(self):
		self.main_from_renderer(partial(gradients, period = 30, speed = 5))

@PatternPlayer.subcommand("gradients")
class GradientsFastCLI(cli.Application, PatternPlayerMixin):
	"""
	Create linear gradients with provided parameters.
	"""
	def main(self, period, speed):
		self.main_from_renderer(partial(gradients, period = period, speed = speed))

def gradients(writer, period, speed):
	"""
	Creates random linear gradients emanating from the centre.

	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	period = float(period)
	speed = int(speed)
	colour = np.zeros(3)
	next_colour = map(int, np.random.random(3)*255)

	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		while True:
			for i in xrange(speed):
				if count % period == 0:
					next_colour = map(int, np.random.random(3)*255)
				colour = colour + (next_colour - colour) / period
				screen[:, :-1, :] = screen[:,1:,:]
				screen[:, -1, :] = colour
				count += 1
			writer_buf_reshaped[:,:,:] = screen
			writer.frame_ready()

def gradients_perlin(writer, period, speed):
	"""
	Creates random Perlin-noise gradients emanating from centre.
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	period = float(period)
	speed = int(speed)
	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		while True:
			for i in xrange(speed):
				r = noise.snoise2(1, count/period) * 128 + 128
				g = noise.snoise2(2, count/period) * 128 + 128
				b = noise.snoise2(3, count/period) * 128 + 128
				colour = (r, g, b)

				screen[:, :-1, :] = screen[:,1:,:]
				screen[:, -1, :] = colour
				count += 1
			writer_buf_reshaped[:,:,:] = screen
			writer.frame_ready()
