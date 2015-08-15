import numpy as np
import colorsys
import random
import math
import cv2
import collections

from functools import partial
from skyscreen_core.interface import Screen, pixel_vane_mapping
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("kaleidoscope-pokemon")
class KaleidoscopePokemonCLI(cli.Application, PatternPlayerMixin):
	"""
	aosnethu
	"""
	def loadPokemons():
		path = "data/pokemon/"
		print "Loading pokemons for kaleidoscope-pokemon"
		pokemons = []
		for x in xrange(1, 151):
			img = cv2.imread(path + str(x) + ".png")
		#	img[np.all(img == [0,0,0], axis=2)] = [10]*3	
			img = np.pad(img, ((1, 1), (1, 1), (0, 0)), 'constant', constant_values=255)
			mask = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)
			cv2.floodFill(img, mask, (0, 0), 0)
			pokemons.append(cv2.resize(img, (50, 50)))
		print "Loaded pokemons for kaleidoscope-pokemon"
		return pokemons
	pokemons = loadPokemons()
	def main(self):
		k = Kaleidoscope(window_size = 60, rotate = -1)
		k.addGenerator(risingPokemon, 100)
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-circles")
class KaleidoscopeCirclesCLI(cli.Application, PatternPlayerMixin):
	"""
	aosnethu
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = -1)
		k.addGenerator(risingCircle, 20)
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-squares")
class KaleidoscopeSquaresCLI(cli.Application, PatternPlayerMixin):
	"""
	aosnethu
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = -1)
		k.addGenerator(fallingSquare, 10)
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

@PatternPlayer.subcommand("kaleidoscope-combined")
class KaleidoscopeCombinedCLI(cli.Application, PatternPlayerMixin):
	"""
	Kaleidoscope with lines, triangles AND circles.
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = -1)
		k.addGenerator(movingLine, 50, {"speed": 2, "thickness": 1, "max_wave_amp": 100})
		k.addGenerator(morphingTriangle, 80, {"speed": 1})
		k.addGenerator(morphingCircle, 20)
		k.addGenerator(snake, 80, {"length": 50, "width": 9, "speed": 3, "x": 2})
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

@PatternPlayer.subcommand("kaleidoscope-bubbles")
class KaleidoscopeBubblesCLI(cli.Application, PatternPlayerMixin):
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
		k.addGenerator(movingLine, 10, {"speed": 4, "thickness": 2, "max_wave_amp": 100})
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

@PatternPlayer.subcommand("kaleidoscope-snake")
class KaleidoscopeSnakeCLI(cli.Application, PatternPlayerMixin):
	"""
	"""
	def main(self):
		k = Kaleidoscope(window_size = 20, rotate = 0)
		k.addGenerator(snake, 80, {"length": 50, "width": 9, "speed": 3, "x": 2})
		k.addGenerator(snake, 160, {"length": 100, "width": 18, "speed": 1})
		self.main_from_renderer(lambda writer: kaleidoscope_renderer(writer, k))

def rotate_screen(screen, x):
	return np.concatenate([screen[x:, : , :], screen[:x, :, :]])

class snake():
	def __init__(self, shape, length, width, speed = 1, x = 0):
		self.q = collections.deque([(x, 0)] * length)
		self.colour = map(int, np.random.random(3) * 255)
		self.shape = shape
		self.width = width
		self.speed = speed
		self.t = 0
		self.s = 0
	def draw(self, screen):
		for x in self.q:
			screen[x[1]][x[0]] = self.colour
	def move(self):
		for x in xrange(self.speed):
			self.q.popleft()	
			if len(self.q) == 0:
				return
			if self.t % (4 * self.width) < self.width:
				(r, c) = np.array(self.q[-1]) + (0, 1)
			elif self.t % (4 * self.width) < 2*self.width:
				(r, c) = np.array(self.q[-1]) + (1, 0)
			elif self.t % (4 * self.width) < 3*self.width:
				(r, c) = np.array(self.q[-1]) + (0, -1)
			else:
				(r, c) = np.array(self.q[-1]) + (1, 0)
			if r < Screen.screen_max_magnitude:
				self.q.append((r, c))
			self.t += 1
	def keep(self):
		return len(self.q) > 0

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

def overlay(base, img, x, y):
	(W, H) = base.shape[:2]
	(w, h) = img.shape[:2]
	h = min(h, H-y)
	base[x:(x+w), y:(y+h), :] = img[:w, :h]

class risingPokemon():
	def __init__(self, shape):
		self.img = np.random.randint(0, 151) #np.random.choice(KaleidoscopePokemonCLI.pokemons)
		#self.p = np.array([shape[1]-1, np.random.random()*shape[0]])
		self.p = [0, 230]
		self.speed = 2
	def draw(self, screen):
		overlay(screen, KaleidoscopePokemonCLI.pokemons[self.img], self.p[0], self.p[1])
	def move(self):
		self.p[1] -= self.speed
	def keep(self):
		return self.p[1] >= 0

class risingCircle():
	def __init__(self, shape):
		self.p = np.array([shape[1]-1, np.random.random()*shape[0]])
		self.speed = np.random.random()*2 + 0.5
		self.decay = 0.98
		self.colour = np.random.random(3) * 255
		self.shape = shape
		self.radius = int(np.random.random()*10 + 5)

	def draw(self, screen):
		(rows, cols) = screen.shape[:2]
		cv2.circle(screen, tuple(map(int, self.p)), self.radius, map(int, self.colour), -1)

	def move(self):
		self.p[0] -= self.speed
		self.colour *= self.decay
	
	def keep(self):
		return (self.p[0] + self.radius > 0)

class fallingSquare():
	def __init__(self, shape):
		self.p = np.array([0, np.random.random()*shape[0]])
		self.speed = np.random.random()*3 + 2
		self.colour = map(int, np.random.random(3) * 255)
		self.shape = shape
		self.width = int(np.random.random()*10 + 5)

	def draw(self, screen):
		(rows, cols) = screen.shape[:2]
		cv2.rectangle(screen, tuple(map(int, self.p)), tuple(map(int, self.p + [10, 10])), self.colour, -1)

	def move(self):
		self.p[0] += self.speed
	
	def keep(self):
		return True #(self.p[0] < self.shape[1])

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
