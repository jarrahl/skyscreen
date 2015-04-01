import logging
import os
import mmap
import skyscreen.interface


class BaseMMapInterface(object):
	def __init__(self, shared_file, using_array_semaphore=None):
		self.using_array_semaphore = using_array_semaphore
		self.shared_file = shared_file
		self.shared_handle = None
		self.shared_memory = None

	def __exit__(self, type, value, traceback):
		assert self.shared_memory is not None, 'already closed, or never opened'
		self.shared_memory.close()
		os.close(self.shared_handle)
		self.shared_handle = None
		self.shared_memory = None


class MMAPScreenWriter(BaseMMapInterface, skyscreen.interface.ScreenWriter):
	file_mode = os.O_CREAT | os.O_TRUNC | os.O_RDWR

	def __enter__(self):
		array_size = skyscreen.interface.Screen.screen_vane_count * skyscreen.interface.Screen.screen_vane_length
		assert self.shared_memory is None, 'cannot open shared mem twice'
		self.shared_handle = os.open(self.shared_file, self.file_mode)
		assert self.shared_handle, 'could not open: %s' % self.shared_file
		assert os.write(self.shared_handle, '\x00' * array_size) == array_size
		self.shared_memory = mmap.mmap(self.shared_handle, array_size, mmap.MAP_SHARED, mmap.PROT_WRITE)
		if self.using_array_semaphore:
			self.using_array_semaphore.acquire()
		return self.shared_memory

	def flush(self, blocking=False):
		if self.using_array_semaphore:
			logging.warning('Releasing the useage semaphore')
			self.using_array_semaphore.release()
			logging.warning('Released the useage semaphore, waiting to acquire it again')
			res = self.using_array_semaphore.acquire(blocking=blocking)
			logging.warning('Re-acquired the usage semaphore')
			return res
		else:
			return True

class MMAPScreenReader(BaseMMapInterface, skyscreen.interface.ScreenReader):
	file_mode = os.O_RDONLY

	def __enter__(self):
		array_size = skyscreen.interface.Screen.screen_vane_count * skyscreen.interface.Screen.screen_vane_length
		assert self.shared_memory is None, 'cannot open shared mem twice'
		self.shared_handle = os.open(self.shared_file, self.file_mode)
		assert self.shared_handle, 'could not open: %s' % self.shared_file
		self.shared_memory = mmap.mmap(self.shared_handle, array_size, mmap.MAP_SHARED, mmap.PROT_READ)
		return self.shared_memory

	def acquire(self, blocking=False):
		if self.using_array_semaphore:
			logging.warning('')
			self.using_array_semaphore.acquire()

	def doneread(self):
		self.using_array_semaphore.release()
