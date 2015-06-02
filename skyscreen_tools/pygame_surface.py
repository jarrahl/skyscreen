import logging
import skyscreen_core.interface as core

SUPPORTED = False
try:
	import pygame
	SUPPORTED = True
except ImportError:
	logging.critical('Pygame not found, the pygame '
					 'wrappers will not work')


class PygameWritingWrapper(core.ScreenWriter):
	"""
	Create a pyGame surface on which you can have your fun.

	You need to pass in another writer, which should itself
	yield a numpy array, and that array must have at least
	3 dimensions (RGB). We create a surface from that, and
	return that to you.

	You can use all the normal pyGame functions! However, you
	should not use the pyGame event loop - leave that to us. But that's
	not really a problem. All that event loop stuff is just for hardware
	rendering, which we're handling in our own special way.
	"""

	def __init__(self, writer):
		self.writer = writer
		self.surf = None
		self.pixels = None

	def __enter__(self):
		self.buf = self.writer.__enter__()
		assert len(self.buf.shape) == 3
		surfsize = self.buf.shape[:2]
		self.surf = pygame.Surface(size=surfsize)
		self.pixels = pygame.surfarray.pixels3d(self.surf)
		return self.surf

	def newsurf(self):
		"""
		Sometimes you loose track of your surface. You overwite
		it or you mess it up or whatever. That's cool. Just call
		newsurf, and we'll return a new one. But remember - we'll
		be ignoring the old one, so don't use it any more.

		Now, this can lead to some really weird looking code in
		a context manager::

			wrapper = PygameWritingWrapper(writer)
			with wrapper as surf:
				...
				surf = wrapper.newsurf()

		Just be cool, and play along as if nothing has happened
		:return: a new surface
		"""
		surfsize = self.buf.shape[:2]
		self.surf = pygame.Surface(size=surfsize)
		self.pixels = pygame.surfarray.pixels3d(self.surf)
		return self.surf

	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self.writer, '__exit__'):
			self.writer.__exit__(exc_type, exc_val, exc_tb)

	def frame_ready(self):
		self.buf[:] = self.pixels
		self.writer.frame_ready()
