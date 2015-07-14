import numpy as np
import math
from skyscreen_core.interface import Screen

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin


@PatternPlayer.subcommand("stars")
class StarsCLI(cli.Application, PatternPlayerMixin):
	"""
	Attempts to recreate the glory of the Windows 98 screen saver.
	"""

	def main(self):
		self.main_from_renderer(starsMain)

def drawStars(stars):
	screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
	for star in stars:
		if (int(star[1]) < Screen.screen_max_magnitude):
			dir_array = [(0,0)]
			if star[1] < 100: # Is the star close?
				dir_array = [(0,0),(0,-1),(0,-2),(0,-3)] # How to draw a close star?
			for d in dir_array: 
				tx = star[0]+d[0]
				ty = star[1]+d[1]
				if tx >= 0 and tx < Screen.screen_vane_count and \
				   ty >= 0 and ty < Screen.screen_max_magnitude:
					screen[tx][ty] = [255] * 3
	return screen


# How far behind the 'zero line' (the innermost circle) should the stars pretend to start?
offset = 10

def speed(d):
	return (d+offset+1) / 20.0

def moveStars(stars):
	for i in xrange(len(stars)):
		stars[i] = (stars[i][0], stars[i][1] - speed(Screen.screen_max_magnitude - stars[i][1]))

def starsMain(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		stars = []
		while True:
			for i in xrange(2): # Increase '2' for moar starz
				stars.append((int(np.random.random() * Screen.screen_vane_count), Screen.screen_max_magnitude + offset))

			writer_buf_reshaped[:, :, :] = drawStars(stars)
			writer.frame_ready()
			moveStars(stars)
			stars = [x for x in stars if x[1] >= 0]


