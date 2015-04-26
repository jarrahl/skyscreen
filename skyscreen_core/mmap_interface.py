"""
This is a reference implementation of the readers and writers.

It's very slow, but it's so simple that we couldn't possibly get it wrong :P

It's used for testing against it. You know your reader is good if it works with
the reference writer implementation, and you know your writer is good if it works
with the reference reader implementation.
"""
import logging
import os
import mmap
import skyscreen_core.interface


class BaseMMapInterface(object):
	def __init__(self, shared_file):
		self.shared_file = shared_file
		self.shared_handle = None
		self.shared_memory = None

	def __exit__(self, type, value, traceback):
		assert self.shared_memory is not None, 'already closed, or never opened'
		self.shared_memory.close()
		os.close(self.shared_handle)
		self.shared_handle = None
		self.shared_memory = None


class MMAPScreenWriter(BaseMMapInterface, skyscreen_core.interface.ScreenWriter):
	file_mode = os.O_CREAT | os.O_RDWR

	def __init__(self, shared_file, lock):
		super(MMAPScreenWriter, self).__init__(shared_file)
		self.lock = lock

	def initialize_file(self):
		self.shared_handle = os.open(self.shared_file, self.file_mode)
		assert self.shared_handle, 'could not open: %s' % self.shared_file
		assert os.write(self.shared_handle, '\x00' * self.array_size) == self.array_size

	def __enter__(self):
		assert self.shared_memory is None, 'cannot open shared mem twice'
		self.initialize_file()
		self.shared_memory = mmap.mmap(self.shared_handle, self.array_size, mmap.MAP_SHARED, mmap.PROT_WRITE)
		return self.shared_memory

	def frame_ready(self):
		self.lock.frame_read()

class MMAPScreenReader(BaseMMapInterface, skyscreen_core.interface.ScreenReader):
	file_mode = os.O_RDONLY

	def __init__(self, shared_file, lock):
		super(MMAPScreenReader, self).__init__(shared_file)
		self.lock = lock

	def __enter__(self):
		assert self.shared_memory is None, 'cannot open shared mem twice'
		try:
			self.shared_handle = os.open(self.shared_file, self.file_mode)
		except OSError:
			logging.error('Got an OS error. Generally this means that '
						  'the reader cannot access the shared file,'
						  'and you need to set up the writer and call'
						  'it\'s initalize method first')
			raise

		assert self.shared_handle, 'could not open: %s' % self.shared_file
		self.shared_memory = mmap.mmap(self.shared_handle, self.array_size, mmap.MAP_SHARED, mmap.PROT_READ)
		return self.shared_memory

	def start_read(self):
		self.lock.start_read()

	def finish_read(self):
		self.lock.finish_read()
