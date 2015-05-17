import numpy as np
from skyscreen_core.interface import Screen

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin


@PatternPlayer.subcommand("chaos")
class ChaosCLI(cli.Application, PatternPlayerMixin):
	"""
	Display the 'chaos' pattern, but it isn't really anything interesting.
	"""

	def main(self):
		self.main_from_renderer(chaos)


def chaos(writer):
	"""
	An attempt at using chaos theory to render cool patterns.
	It didn't really go anywhere.

	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		row = 0.5
		col = 1.0
		rate = 3.66
		floating_version = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude))

		while True:
			print row, col, rate * row * (1 - row)
			floating_version[:] = floating_version * 0.999
			floating_version[(Screen.screen_vane_count - 1) * row, col] = 255

			row = (rate * row * (1 - row))
			col = (row + col) % Screen.screen_max_magnitude
			color = (row * Screen.screen_vane_count) % 3
			writer_buf_reshaped[:, :, color] = np.floor(floating_version)
			writer.frame_ready()