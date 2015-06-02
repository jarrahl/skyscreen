import skyscreen_tools.flatspace
import skyscreen_tools.pygame_surface
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

import pygame


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
			surf.fill((255, 0, 0))
			t += 1

