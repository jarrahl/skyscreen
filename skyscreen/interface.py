import mmap_interface
import os
import threading


class Screen(object):
	screen_vane_length = 144 * 2
	screen_vane_count = 360


class ScreenBuffer(object):
	"""An abstract screen buffer"""

	def __getitem__(self, item):
		raise NotImplementedError()

	def __setitem__(self, key, value):
		"""This may fail when passed back by a screen reader"""
		raise NotImplementedError()


class ScreenWriter(Screen):
	def __enter__(self):
		"""
		:return: a ScreenBuffer
		"""
		raise NotImplementedError()

	def __exit__(self, type, value, traceback):
		raise NotImplementedError()

	def flush(self):
		raise NotImplementedError()

class ScreenReader(Screen):
	def __enter__(self):
		"""
		:return: a ScreenBuffer
		"""
		raise NotImplementedError()

	def __exit__(self, type, value, traceback):
		raise NotImplementedError()

	def read(self):
		raise NotImplementedError()

	def doneread(self):
		raise NotImplementedError()

class WriterSync(object):
	def acquire(self):
		pass

	def release(self):
		pass