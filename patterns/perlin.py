import numpy as np
import math
import colorsys
import random
import noise
from functools import partial

from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

R = Screen.screen_max_magnitude
C = Screen.screen_vane_count
count = 0

def bloom(x):
	m = (np.array([5, 3, 2]) * x) % 1.0
	m = m*m*m
	return m * 256

def bluegreen(x):
	m = [0.682, 0.193, 0.711]
	return [256*(x % a) / a for a in m]

def cytoplasm(x):
	m = [0.1234, 0.4231, 0.6193]
	return [256*(x % a) / a for a in m]

def persian(x):
	if x % 0.1 < 0.05:
		return [255]*3
	else:
		return [0]*3

def supernova(x):
	# x is in [-1,1]
	return np.array(colorsys.hsv_to_rgb(x, 1, 1)) * 255

def spaceribbons(x):
	if x < -0.2 or x > 0.2:
		if x % 0.01 < 0.0005:
			return [int(255 * (x % 0.03) / 0.03)] * 3
		return [0]*3
	if x < 0.2:
		x = (x + 0.2) / 0.4
		return [255 * (x % 0.2) / 0.2, 255 * (x % 0.3) / 0.3, 255 * (x % 0.13) / 0.13]
	return [255]*3

	prev = -1.0
	for (threshold, func) in a:
		if x <= threshold:
			return func((x - prev) / (threshold - prev))
		prev = threshold

def spaceclouds(x):
	x = (x + 1)/2
	t = [0.4, 0.55, 0.6,0.62]
	if x < t[0]:
		return [0]*3
	if x < t[1]:
		return [0, 0, 255 * (x-t[0]) / (t[1] - t[0])]
		#return [0, 0, max(0, min(1, 1.1 * math.log(3*x - t)))*255]
	if x < t[2]:
		y = 255 * (x - t[1]) / (t[2] - t[1])
		return [y, y, 255]
	if x < t[3]:
		y = 255 * (1.0 - (x - t[2]) / (t[3] - t[2]))
		return [y, y, y]
	return [0] * 3

def pinksky(x):
	orchid = np.array([128, 0, 128])
	if x < -0.2:
		return orchid
	if x < 0:
	#	return [0,0,255]
		return orchid + ((x+0.2)/0.2) * (np.array([0, 0, 255]) - orchid)
	if x < 0.2:
		return [0,0,255]
	return [0,0,(0.8 - x) * 255]

@PatternPlayer.subcommand("perlin-kaleido-bloom")
class PerlinKaleidoBloomCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 30, colour = bloom, r = 1, iterations = 5, rotate = 0.2, speed = 2))

@PatternPlayer.subcommand("perlin-kaleido-bottles")
class PerlinKaleidoBottlesCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 5, colour = bluegreen, r = 1, iterations = 5, rotate = 0.2, speed = 2))
@PatternPlayer.subcommand("perlin-kaleido-cytoplasm")
class PerlinKaleidoCytoplasmCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = cytoplasm, r = 1, iterations = 5, rotate = -0.2, speed = 2))
@PatternPlayer.subcommand("perlin-kaleido-persian")
class PerlinKaleidoPersianCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = persian, r = 1, iterations = 5, rotate = -0.1, speed = 2))
@PatternPlayer.subcommand("perlin-kaleido-pinksky")
class PerlinKaleidoPinkskyCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = pinksky, r = 1, iterations = 5, rotate = 0.2, speed = 3))
@PatternPlayer.subcommand("perlin-kaleido-supernova")
class PerlinKaleidoSupernovaCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = supernova, r = 1, iterations = 5, rotate = -0.25, speed = 2))
@PatternPlayer.subcommand("perlin-kaleido-spaceclouds")
class PerlinKaleidoSpacecloudsCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = spaceclouds, r = 1, iterations = 5, rotate = 0, speed = 2))
@PatternPlayer.subcommand("perlin-kaleido-spaceribbons")
class PerlinKaleidoSpaceribbonsCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_kaleido_gen, pane_size = 20, colour = spaceribbons, r = 1, iterations = 5, rotate = 0, speed = 2))

@PatternPlayer.subcommand("perlin-cytoplasm")
class PerlinCytoplasmCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = cytoplasm, r = 1, iterations = 5, rotate = -0.2, speed = 2))
@PatternPlayer.subcommand("perlin-persian")
class PerlinPersianCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = persian, r = 1, iterations = 5, rotate = -0.1, speed = 2))
@PatternPlayer.subcommand("perlin-pinksky")
class PerlinPinkskyCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = pinksky, r = 1, iterations = 5, rotate = 0.3, speed = 5))

@PatternPlayer.subcommand("perlin-supernova")
class PerlinSupernovaCLI(cli.Application, PatternPlayerMixin):
	"""
	Supernova: watch the inside of a star explode above you eternally
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = supernova, r = 0.5, iterations = 5, rotate = 0))

@PatternPlayer.subcommand("perlin-spaceribbons")
class PerlinSpaceribbonsCLI(cli.Application, PatternPlayerMixin):
	"""
	Space ribbons: connected ribbons of rainbows... IN SPACE
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = spaceribbons, r = 1, iterations = 2, rotate = 0))

@PatternPlayer.subcommand("perlin-spaceclouds")
class PerlinCloudsCLI(cli.Application, PatternPlayerMixin):
	"""
	Space clouds: Inspired by Doctor Who intro, blue-white-black colour scheme of clouds
	"""
	def main(self):
		self.main_from_renderer(partial(perlin_gen, colour = spaceclouds, r = 1, iterations = 3, rotate = 0, speed = 10))

def f(x, y, colour, r, iterations):
	return colour(noise.snoise3(r*math.sin(2 * math.pi * x/C), r*math.cos(2 * math.pi * x/C), float(y)/R, iterations))
	#return colour(noise.pnoise3(r*math.sin(2 * math.pi * x/C), r*math.cos(2 * math.pi * x/C), float(y)/R, iterations))

def rotate_screen(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

def perlin_gen(writer, colour, r = 1.0, iterations = 5, rotate = 1, speed = 1):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	global count

	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		screen = np.zeros(writer_buf_reshaped.shape)
		for y in xrange(R):
			for x in xrange(C):
				screen[x, y] = f(x, y, colour, r, iterations) 
		count = R
		while True:
			for i in xrange(speed):
				screen[:, :-1, :] = screen[:, 1:, :]
				for x in xrange(C):
					screen[x, -1] = f(x, count, colour, r, iterations)
				count += 1
			writer_buf_reshaped[:] = rotate_screen(screen, int(rotate * count) % C)
			writer.frame_ready()


def perlin_kaleido_gen(writer, colour, pane_size = 20, r = 1.0, iterations = 5, rotate = 1, speed = 1):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	global count, C

	#C = pane_size
	num_windows = 360 / pane_size / 2
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		screen = np.zeros((pane_size, Screen.screen_max_magnitude, 3))
		for y in xrange(R):
			for x in xrange(pane_size):
				screen[x, y] = f(x, y, colour, r, iterations) 
		count = R
		while True:
			for i in xrange(speed):
				screen[:, :-1, :] = screen[:, 1:, :]
				for x in xrange(pane_size):
					screen[x, -1] = f(x, count, colour, r, iterations)
				count += 1
			writer_buf_reshaped[:,:,:] = rotate_screen(np.vstack([np.vstack((screen, screen[::-1]))] * num_windows),
													   int(rotate * count) % Screen.screen_vane_count)
			writer.frame_ready()

