import numpy as np
import colorsys
import random
import math

from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

DEGREES = 360

@PatternPlayer.subcommand("sinwaves")
class SinWavesCLI(cli.Application, PatternPlayerMixin):
	"""
	Run the sinwaves program.

	Sinwaves radiates coloured circular sinwaves from the centre.
	They are pretty.
	"""
	def main(self):
		self.main_from_renderer(sinwaves)


def CreateWave(amp, freq):
	domain = 2 * freq *  math.pi
	d = [0] * DEGREES
	for i in xrange(DEGREES):
		d[i] = math.sin(domain * float(i) / DEGREES) * (amp/2) + amp/2
	return d

def rotate(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

def sinwaves(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""

	# WE ARE NUMBERS PLAY WITH US!!!

	wave_size = 20 # amplitude of sine waves
	num_freq = 20 # frequency (number of peaks) of sine waves
	wave_gap = 10 # how many pixels to leave between two sine waves
	change_rot_freq = 0 # how often to change rotational direction
	rotation_amount = 0 # max pixels to rotate by


	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		while True:
			if count % wave_gap == 0:
				a = CreateWave(wave_size, num_freq)
				colour = map(int, np.random.random(3) * 255)
				for i in xrange(Screen.screen_vane_count):
					screen[i, a[i] + Screen.screen_max_magnitude - wave_size] = np.array(colour)
			screen[:, :-1, :] = screen[:,1:,:]
			screen[:, -1, :] = 0

			writer_buf_reshaped[:,:,:] = rotate(screen, int(math.sin(count * change_rot_freq) * rotation_amount))
			writer.frame_ready()
			count += 1

