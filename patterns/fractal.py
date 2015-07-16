import numpy as np
import colorsys
import math
import skyscreen_tools
from skyscreen_core.interface import Screen

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("fractal")
class FractalCLI(cli.Application, PatternPlayerMixin):
	"""
	Generates and displays Mandelbrot fractals at increasing zoom levels.
	Unfortunately at any reasonable zoom levels, it is too computationally
	complex and the pattern is unusably laggy.
	"""

	def main(self):
		self.main_from_renderer(fractal)

def mandel(n, m, itermax, xmin, xmax, ymin, ymax):
	ix, iy = np.mgrid[0:n, 0:m]
	x = np.linspace(xmin, xmax, n)[ix]
	y = np.linspace(ymin, ymax, m)[iy]
	c = x+complex(0,1)*y
	del x, y
	img = np.zeros((n, m, 3))
	ix.shape = n*m
	iy.shape = n*m
	c.shape = n*m
	z = np.copy(c)
	for i in xrange(itermax):
		if not len(z): break
		np.multiply(z, z, z)
		np.add(z, c, z)
		rem = abs(z)>2.0
		img[ix[rem], iy[rem]] = np.array(colorsys.hsv_to_rgb(float(i)/itermax, 1, 1)) * 255
		rem = -rem
		z = z[rem]
		ix, iy = ix[rem], iy[rem]
		c = c[rem]
	return img

def fractal(writer):
	"""
	Zooms in to a mandelbrot set. Quickly becomes too slow.

	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	# key parameters:
	# co-ordinate of centre of screen
	centre = (0.437089, -0.34404)
	# initial zoom level (higher number = lower zoom)
	x = 100
	y = 100

	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with reshaped as writer_buf:
		(rows, cols) = writer_buf.shape[:2]
		while True:
			x *= 0.95
			y *= 0.95
			writer_buf[:,:,:] = mandel(rows, cols, 30, centre[0]-x, centre[0]+x, centre[1]-y, centre[1]+y)
			reshaped.frame_ready()
