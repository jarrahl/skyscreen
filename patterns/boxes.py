import math
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
import numpy as np
import cv2
import skyscreen_tools

# The following 3 functions should be CHANGED FOR FUNSIES

# def delay(t):
# How long to wait after time 't' before creating a new box

# def rotateAmount(t):
# How many radians to rotate everything by at time t

# def scaleAmount(t):
# How much to scale each box by at time t

def boxes_pulsar(writer):
	def delay(t):
		return 5
	def rotateAmount(t):
		return math.sin(t/100.0)/50.0
	def scaleAmount(t):
		return math.sin(t/10.0)*0.04 + 0.99
	boxes_renderer(writer, delay, rotateAmount, scaleAmount)

def boxes_swirl(writer):
	def delay(t):
		return 1.0 / (t/10000.0 + 0.05)
	def rotateAmount(t):
		return math.log(t+1)/100.0
	def scaleAmount(t):
		return 0.98
	boxes_renderer(writer, delay, rotateAmount, scaleAmount)

def boxes_boring(writer):
	def delay(t):
		return 20
	def rotateAmount(t):
		return 0.04
	def scaleAmount(t):
		return 0.982
	boxes_renderer(writer, delay, rotateAmount, scaleAmount)

def boxes_infinity(writer):
	def delay(t):
		return 0
	def rotateAmount(t):
		return 0
	def scaleAmount(t):
		return 0.95
	boxes_renderer(writer, delay, rotateAmount, scaleAmount)

@PatternPlayer.subcommand("boxes-pulsar")
class BoxesPulsarCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(boxes_pulsar)

@PatternPlayer.subcommand("boxes-swirl")
class BoxesSwirlCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(boxes_swirl)

@PatternPlayer.subcommand("boxes-boring")
class BoxesBoringCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(boxes_boring)

@PatternPlayer.subcommand("boxes-infinity")
class BoxesInfinityCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(boxes_infinity)

def rotatePoint(p, theta):
	return (p[0] * math.cos(theta) - p[1] * math.sin(theta),
			p[0] * math.sin(theta) + p[1] * math.cos(theta))

class Polygon():
	points = []
	colour = []

	def __init__(self, points):
		self.points = points
		self.colour = [int(x*255) for x in np.random.random(3)]

	def roundPoint(self, i, midx, midy):
		return (int(round(self.points[i][0]+midx)),
				int(round(self.points[i][1]+midy)))

	def rotate(self, theta):
		self.points = [rotatePoint(p, theta) for p in self.points]

	def scale(self, scale):
		self.points = [(p[0]*scale,p[1]*scale) for p in self.points]

	def keep(self):
		return any([p[0] > 1 or p[1] > 1 for p in self.points])

	def draw(self, screen, midx, midy):
		for i in xrange(len(self.points)):
			cv2.line(screen, self.roundPoint(i, midx, midy), 
							 self.roundPoint(i-1, midx, midy),
							 self.colour, 3)

def boxes_renderer(writer, delay, rotateAmount, scaleAmount):
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	t = 0
	polys = []
	with reshaped as writer_buf:
		(rows, cols) = writer_buf.shape[:2]
		midx = rows/2
		midy = cols/2
		next_t = delay(0)
		while True:
			screen = np.zeros((rows, cols, 3))
			for poly in polys:
				poly.draw(screen, midx, midy)
				poly.rotate(rotateAmount(t))
				poly.scale(scaleAmount(t))
			
			polys = [x for x in polys if x.keep()]
			offset = 0 # how far in from the edge should we make the squares
			if t >= next_t:
				polys.append(Polygon([(-(midx - offset), -(midy - offset)),
									  ( (midx - offset), -(midy - offset)),
									  ( (midx - offset),  (midy - offset)),
									  (-(midx - offset),  (midy - offset))]))
				next_t = t + delay(t)

			writer_buf[:,:,:] = screen
			reshaped.frame_ready()
			t += 1
