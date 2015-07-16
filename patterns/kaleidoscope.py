import numpy as np
import colorsys
import random
import math
import cv2

from functools import partial
from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("kaleidoscope-combined")
class KaleidoscopeCombinedCLI(cli.Application, PatternPlayerMixin):
	"""
	Kaleidoscope with lines, triangles AND circles.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = -1)
		k.addGenerator(movingLine, 50, {"speed": 3, "thickness": 2, "max_wave_amp": 100})
		k.addGenerator(morphingTriangle, 80, {"speed": 1})
		k.addGenerator(morphingCircle, 5)
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-triangles")
class KaleidoscopeTrianglesCLI(cli.Application, PatternPlayerMixin):
	"""
	Kaleidoscope with random triangles.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = 1)
		k.addGenerator(morphingTriangle, 20, {"speed": 1})
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-circles")
class KaleidoscopeCirclesCLI(cli.Application, PatternPlayerMixin):
	"""
	Kaleidoscope with random circles.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 45, rotate = 0)
		k.addGenerator(morphingCircle, 5)
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("eye-of-god")
class KaleidoscopeFastLinesCLI(cli.Application, PatternPlayerMixin):
	"""
	Stare at the centre for 1 minute and understand the spirit of God.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 10, rotate = 0.5)
		k.addGenerator(movingLine, 10, {"speed": 4, "thickness": 1, "max_wave_amp": 100})
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-superfast")
class KaleidoscopeSuperFastCLI(cli.Application, PatternPlayerMixin):
	"""
	Kaleidoscope with very fast random lines.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 6, rotate = 0.5)
		k.addGenerator(movingLine, 10, {"speed": 6, "thickness": 1, "max_wave_amp": 200})
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-flowers")
class KaleidoscopeCLI(cli.Application, PatternPlayerMixin):
	"""
	Low-speed relaxing kaleidoscope, a bit like flowers.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = 0)
		k.addGenerator(movingLine, 20, {"speed": 3, "thickness": 2, "max_wave_amp": 100})
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

def rotate_screen(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

class movingLine():
	def __init__(self, shape, speed, max_wave_amp, thickness):
		self.x = -int(np.random.random() * max_wave_amp)
		self.y = -int(np.random.random() * max_wave_amp)
		self.speed = speed
		self.thickness = thickness
		self.colour = map(int, np.random.random(3) * 255)

	def draw(self, screen):
		(rows, cols) = screen.shape[:2]
		cv2.line(screen, (self.x, 0), (self.y, rows-1), self.colour, self.thickness)
	
	def move(self):
		self.x += self.speed
		self.y += self.speed
	
	def keep(self):
		return self.x < Screen.screen_max_magnitude or self.y < Screen.screen_max_magnitude

class morphingTriangle():
	def __init__(self, shape, speed):
		self.p = np.array([np.random.random(2) * shape[::-1] for x in xrange(3)])
		self.speed = np.random.random() * speed
		self.colour = map(int, np.random.random(3) * 255)
		self.shape = shape

	def draw(self, screen):
		(rows, cols) = screen.shape[:2]
		cv2.fillConvexPoly(screen, np.array(self.p, 'int32'), self.colour)
	
	def move(self):
		self.p += self.speed
	
	def keep(self):
		return (self.p < self.shape[0]).any()

class morphingCircle():
	def __init__(self, shape):
		self.p = np.random.random(2) * shape[::-1]
		self.rmax = np.random.random() * 10
		self.r = 1
		self.speed = np.random.random(3) + 0.1
		self.colour = map(int, np.random.random(3) * 255)
		self.shape = shape

	def draw(self, screen):
		(rows, cols) = screen.shape[:2]
		cv2.circle(screen, tuple(map(int, self.p)), int(self.r), self.colour, 1)
	
	def move(self):
		if self.r < self.rmax:
			self.r += self.speed[0]
		else:
			self.p += self.speed[1:]
	
	def keep(self):
		return (self.p < self.shape[0]).any()

class Kaleidoscope():
	def __init__(self, window_size, rotate):
		self.window_size = window_size
		self.rotate = rotate
		self.generators = []
	
	def addGenerator(self, c, delay, args = {}):
		self.generators.append((c, delay, args))


def kaleidoscope_renderer(writer, kaleidoscope):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""

	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		objects = []
		while True:
			screen = np.zeros((kaleidoscope.window_size, Screen.screen_max_magnitude, 3))
			num_windows = Screen.screen_vane_count / kaleidoscope.window_size / 2
			for generator in kaleidoscope.generators:
				if count % generator[1] == 0:
					objects.append(generator[0](screen.shape[:2], **generator[2]))
			for obj in objects:
				obj.draw(screen)
				obj.move()
			objects = [x for x in objects if x.keep()]
			writer_buf_reshaped[:,:,:] = rotate_screen(np.vstack([np.vstack((screen, screen[::-1]))] * num_windows),
													   int(kaleidoscope.rotate * count) % Screen.screen_vane_count)
			writer.frame_ready()
			count += 1
