import numpy as np
import colorsys
import random
import math

from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("fermat-spiral")
class FermatSpiralCLI(cli.Application, PatternPlayerMixin):
	"""
	Run the fermat-spiral program.
	"""
	def main(self):
		self.main_from_renderer(spiral_renderer)

def rotate(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

def spiral_renderer(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""

	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		a = 1.5
		rotation_amount = 4
		while True:
			screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
			#a = (math.sin(count/30.0)/2 + 0.5) * 8 + 5
			a = 13
			print a
			max_angle = int((Screen.screen_max_magnitude/a)**2)
			for theta in xrange(1, max_angle):
				r1 = a * math.sqrt(theta)
				if int(r1) < Screen.screen_max_magnitude:
					screen[theta % 360][-int(r1):-int(r1-3)] = np.array(colorsys.hsv_to_rgb(((theta + count) % 100) / 100.0, 1, 1)) * 255
					screen[(theta + 180) % 360][-int(r1):-int(r1-3)] = screen[theta % 360][-int(r1)]
			writer_buf_reshaped[:,:,:] = rotate(screen, int(count * rotation_amount) % Screen.screen_vane_count)
			writer.frame_ready()
			count += 1

