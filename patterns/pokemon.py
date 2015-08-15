import sys
import math
from math import sin
import numpy as np
from skyscreen_core.interface import Screen
import skyscreen_tools.flatspace
import cv2

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("pokemon")
class PokemonStaticCLI(cli.Application, PatternPlayerMixin):
	"""
	Shows random static images of the first 150 pokemon. The fade-in-out works best with the 'max' combine operation,
	but for full unadulterated pokemon pics you should use the 'mask' combine operation.
	"""

	def main(self):
		self.main_from_renderer(pokemon)

def rotateImage(img, angle):
	center = tuple(np.array(img.shape[:2])/2)
	rot_mat = cv2.getRotationMatrix2D(center, angle, 1)
	return cv2.warpAffine(img, rot_mat, img.shape[:2], flags=cv2.INTER_LINEAR)

def overlay(base, img, x, y):
	(w, h) = img.shape[:2]
	base[x:(x+w), y:(y+h), :] = img

def loadPokemons():
	path = "data/pokemon/"
	print "Loading pokemons"
	pokemons = []
	for x in xrange(1, 151):
		img = cv2.imread(path + str(x) + ".png")
		# Set black pixels to almost-black so they don't get masked out
		img[np.all(img == [0,0,0], axis=2)] = [10]*3	
		# Add a 1-pixel white border so floodFill from one corner gets all corners
		img = np.pad(img, ((1, 1), (1, 1), (0, 0)), 'constant', constant_values=255)

		# We ignore the mask output of floodFill, but it needs an array to output to
		ignored_crap = np.zeros((img.shape[0] + 2, img.shape[1] + 2), dtype=np.uint8)
		# Set the white background to be black, for masking / overlaying
		cv2.floodFill(img, ignored_crap, (0, 0), 0)
		pokemons.append(cv2.resize(img, (450, 450)))
	print "Loaded pokemons"
	return pokemons

def pokemon(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	# Load the pokemans
	pokemons = loadPokemons()

	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with reshaped as writer_buf:
		(rows, cols) = writer_buf.shape[:2]
		count = 0
		screen = np.zeros((rows, cols, 3))
		while True:
			if count % 200 == 0:
				x = np.random.randint(150)
				screen[:,:,:] = 0
				overlay(screen, pokemons[x], 100, 100)
			writer_buf[:,:,:] = screen * min(1, min(count%200, 200 - count%200) / 50.0)
			reshaped.frame_ready()
			count += 1
