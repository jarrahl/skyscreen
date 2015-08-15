import numpy as np
from functools import partial
import colorsys
import random
import math
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
from skyscreen_core.interface import Screen
from math import sin, cos
#import noise

DEGREES = 360

# TODO(jarrah): still a work in progress here, a few ideas still to come

@PatternPlayer.subcommand("otto")
class OttoCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		self.main_from_renderer(otto)

class SinLine():
	def __init__(self, x, freq, amplitude):
		self.x = x
		self.freq = freq
		self.amplitude = amplitude
		self.t = 0
		self.colour = map(int, np.random.random(3)*256)
	def draw(self, line):
		y = (sin(self.t * self.freq) + 1) * self.amplitude
		line[min(360, 360 + self.x - y):] = self.colour
		line[max(0, self.x - y) : min(360, self.x + y)] = self.colour
		line[: max(0, self.x + y - 360)] = self.colour
	def move(self):
		self.t += 1
	def keep(self):
		return self.t < 1000

class SinLine():
	def __init__(self, x, freq, amplitude):
		self.x = x
		self.freq = freq
		self.amplitude = amplitude
		self.t = 0
		self.colour = np.random.random(3)*256
		self.prevy = x
		self.lifespan = 1000
	def draw(self, line):
		colour = map(int, self.colour * min(1.0, min(self.t, self.lifespan - self.t) / 100.0))
		y = round(sin(self.t * self.freq) * self.amplitude + self.x + self.t + 360) % 360
		(a, b) = sorted([y, self.prevy])
		if b - a > 180:
			line[b:] = colour
			line[:a+1] = colour
		else:
			line[a:b+1] = colour
		self.prevy = y
	def move(self):
		self.t += 1
	def keep(self):
		return True #self.t < 1000
	
class MovingDot():
	def __init__(self, x):
		self.x = x
		self.colour = map(int, np.random.random(3)*256)
		self.t = 0
	def draw(self, line):
		line[self.x] = self.colour
	def move(self):
		self.x = (self.x + 1) % 360
		self.t += 1
	def keep(self):
		return self.t < 10000

def rotate_screen(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

def otto(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""

	with writer as writer_buf:
		screen = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

		count = 0
		speed = 2
		objects = []
		for x in xrange(10):
			objects.append(SinLine(x * 36, np.random.random() * 0.03 + 0.1, np.random.random()*20 + 1))
	#		objects.append(SinLine(x * 36, 0.4, 10))
			#objects.append(MovingDot(int(np.random.random()*360)))
		while True:
			#if count % 3000 == 0:
				#objects.append(SinLine(int(np.random.random()*360)))
			#	objects.append(SinLine(int(np.random.random()*360), 0.4, 10))
			for i in xrange(speed):
				screen[:, :-1, :] = screen[:, 1:, :]
				screen[:, -1, :] = 0
				for obj in objects:
					obj.draw(screen[:, -1])
					obj.move()
				objects = [x for x in objects if x.keep()]
				count += 1
			writer_buf_reshaped[:,:,:] = rotate_screen(screen, int(count / 3.0) % 360)
			writer_buf_reshaped[:, -1, :] = 150
			writer.frame_ready()
