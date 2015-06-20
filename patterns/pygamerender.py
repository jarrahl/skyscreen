from random import random
import skyscreen_tools.flatspace
import skyscreen_tools.pygame_surface
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
import numpy as np
import pygame
import scipy.spatial
import line_profiler


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

	def main(self, nbirds=250, npredators=3):
		self.nbirds = int(nbirds)
		self.npredators = int(npredators)
		self.main_from_renderer(self.birds)

	def birds(self, writer):
		reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
		#reshaped = skyscreen_tools.reshape_wrapper.ReshapingWriterWrapper(writer)
		surfWriter = skyscreen_tools.pygame_surface.PygameWritingWrapper(reshaped)
		with surfWriter as surf:
			self.surf = surf
			# Initialize our flock
			self._initialize_flock(
				surf.get_width(),
				surf.get_height())

			while True:
				for bird in self.flock_location:
					pygame.draw.rect(surf, (255, 255, 255), (bird[0], bird[1], 3, 3))
				for predator in self.predator_location:
					pygame.draw.rect(surf, (255, 0, 0), (predator[0], predator[1], 3, 3))
				self.step_flock()
				surfWriter.frame_ready()
				surf.fill((0, 0, 0))

	def _initialize_flock(self, width, height):
		# Create a flock of randomly placed birds
		self.flock_location = np.random.random(size=(self.nbirds, 2)) * np.array([width, height])
		self.flock_velocity = np.random.normal(size=(self.nbirds, 2))

		self.predator_location = np.random.random(size=(self.npredators, 2)) * np.array([width, height])
		self.predator_velocity = np.random.normal(size=(self.npredators, 2))


	def step_flock(self):
		interflock_distances = scipy.spatial.distance.squareform(
			scipy.spatial.distance.pdist(self.flock_location)
		)
		interflock_neighbourhoods = (interflock_distances < 40) & \
									(interflock_distances >= 20) & \
									np.invert(np.eye(self.flock_location.shape[0], dtype=bool))

		interflock_tooclose = (interflock_distances < 20) & \
							  np.invert(np.eye(self.flock_location.shape[0], dtype=bool))

		predator_distances = scipy.spatial.distance.cdist(self.flock_location, self.predator_location)
		tooclose_predators = predator_distances < 80

		# For each bird:
		# 1. Observe the set of neighbours
		# 2. Observe their velocity, and take the average
		# 3. And also adjust our velocity towards the group center
		# 4. Adjust the velocity away from any bird that's too close

		for ix, bird in enumerate(self.flock_location):
			local_birds, = np.nonzero(interflock_neighbourhoods[ix])
			tooclose_birds, = np.nonzero(interflock_tooclose[ix])
			tooclose_predator, = np.nonzero(tooclose_predators[ix])
			if local_birds.size == 0:
				locality_inclusion_vector = np.zeros(2)
				# If there are no close neighbours, we use our velocity
				locality_velocity = self.flock_velocity[ix]
			else:
				locality_velocity = np.mean(self.flock_velocity[local_birds], axis=0)
				locality_center = np.mean(self.flock_location[local_birds], axis=0)
				locality_inclusion_vector = np.tanh(locality_center - bird)

			if tooclose_birds.size != 0:
				tooclose_center = np.mean(self.flock_location[tooclose_birds], axis=0)
				# tooclose_escape_vector = np.exp(bird - tooclose_center) # Interesting outcome
				tooclose_escape_vector = 1 / (0.1 * (bird - tooclose_center))
			else:
				tooclose_escape_vector = np.zeros(2)

			if tooclose_predator.size != 0:
				predator_center = np.mean(self.predator_location[tooclose_predator], axis=0)
				predator_escape_vector = 1 / (0.1 * (bird - predator_center))
			else:
				predator_escape_vector = np.zeros(2)

			new_velocity = np.clip(
				locality_velocity +
				0.1 * locality_inclusion_vector +
				0.2 * tooclose_escape_vector +
				0.5 * predator_escape_vector +
				0.1 * np.random.normal(size=2), -2, 2)
			self.flock_velocity[ix] = new_velocity
		self.flock_location += self.flock_velocity / 2

		if np.random.random() < 0.01:
			self.predator_velocity = np.random.normal(size=self.predator_velocity.shape)
		self.predator_location += self.predator_velocity

		self.flock_location = np.mod(self.flock_location, self.surf.get_width())
		self.predator_location = np.mod(self.predator_location, self.surf.get_width())
