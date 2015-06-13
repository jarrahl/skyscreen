from random import random
import skyscreen_tools.flatspace
import skyscreen_tools.pygame_surface
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
import numpy as np
import pygame
import scipy.spatial

@PatternPlayer.subcommand("pygame")
class PyGameTest(cli.Application, PatternPlayerMixin):
	"""
	Render a video to the skyscreen
	"""

	def main(self):
		self.main_from_renderer(pygamerender)


def pygamerender(writer):
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	surfWriter = skyscreen_tools.pygame_surface.PygameWritingWrapper(reshaped)
	t = 0
	with surfWriter as surf:
		while True:
			pygame.draw.rect(surf, (t % 255, 255, 255), (150, 150, t % 50, t % 50))
			surfWriter.frame_ready()
			surf.fill((0, 255, 0))
			t += 1


@PatternPlayer.subcommand("flock")
class Flock(cli.Application, PatternPlayerMixin):
	"""
	Make a flock of birds. They fly around and around and stay together.

	We'll create a lead bird, that files a random path, and then all the
	other birds aim to keep a good separation between each other, while
	staying close to the lead bird
	"""

	def main(self, nbirds=25):
		self.nbirds = nbirds
		self.main_from_renderer(self.birds)

	def birds(self, writer):
		reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
		surfWriter = skyscreen_tools.pygame_surface.PygameWritingWrapper(reshaped)
		with surfWriter as surf:
			# Initialize our flock
			self._initialize_flock(
				surf.get_width(),
				surf.get_height())

			while True:
				for bird in self.flock_location:
					pygame.draw.rect(surf, (255,255,255), (bird[0], bird[1], 3, 3))
				pygame.draw.rect(surf, (255, 0, 0), (self.lead_bird_location[0], self.lead_bird_location[1], 3, 3))
				self.step_flock()
				surfWriter.frame_ready()
				surf.fill((0, 0, 255))

	def _initialize_flock(self, width, height):
		# Create a lead bird in a random location
		self.lead_bird_location = np.random.random(size=2) * np.array([width, height])
		self.lead_bird_velocity = np.random.random(size=2)
		# Create a flock of randomly placed birds
		self.flock_location = np.random.random(size=(self.nbirds, 2)) * np.array([width, height])
		self.flock_velocity = np.random.random(size=(self.nbirds, 2))

	def step_flock(self):
		self.lead_bird_location = np.mod((self.lead_bird_location * self.lead_bird_velocity), 500)
		print self.lead_bird_location
		self.lead_bird_velocity += np.random.normal(size=2)
		self.lead_bird_velocity = self.lead_bird_velocity / np.linalg.norm(self.lead_bird_velocity)

		# To move the other birds, we wish to pick a vector
		# for direction that brings the bird back towards the leader,
		# except that the birds are repelled from each other with
		# a strength, proportional to the inverse square of the distance
		# to the other birds. In cases where the distance is zero, we
		# will pick a random direction to fly in.

		#interflock_distances = scipy.spatial.distance.squareform(
		#	scipy.spatial.distance.pdist(self.flock_location))
		#lead_distance = scipy.spatial.distance.cdist(
		#	self.flock_location,
		#	self.lead_bird_location)

		# We now apply our distance function, given by the log of the distance
		# the function is negative for distances less than one, and gently
		# positive for distances greater than one.

		#interflock_attraction_factors = np.log(interflock_distances)
		#lead_attraction_factors = np.log(lead_distance)

		# Now, we find the normalized direction vector between each member of the flock
		# This ends up being a tensor though. It's a bit weird.

		for ix, bird in enumerate(self.flock_location):
			directions = self.flock_location - bird
			lengths = np.linalg.norm(directions, axis=1).reshape((len(directions), 1))
			attraction_factors = np.log(lengths/1000)
			attraction_factors[ix] = 0
			self.flock_velocity[ix, :] += np.dot(directions.T, attraction_factors).flatten()
			lead_length = np.linalg.norm(self.lead_bird_location - self.flock_location[ix])
			lead_attraction_factor = np.log(lead_length)*10
			self.flock_velocity[ix] += (self.lead_bird_location - self.flock_location[ix]) * lead_attraction_factor

		self.flock_velocity /= np.linalg.norm(self.flock_velocity, axis=1).reshape(self.flock_velocity.shape[0], 1)
		self.flock_location += self.flock_velocity