import logging
import os
import mmap
import skyscreen.interface


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


class MMAPScreenWriter(BaseMMapInterface, skyscreen.interface.ScreenWriter):
	file_mode = os.O_CREAT | os.O_RDWR

	def __init__(self, shared_file):
		super(MMAPScreenWriter, self).__init__(shared_file)

	def initialize_file(self):
		self.shared_handle = os.open(self.shared_file, self.file_mode)
		assert self.shared_handle, 'could not open: %s' % self.shared_file
		assert os.write(self.shared_handle, '\x00' * self.array_size) == self.array_size

	def __enter__(self):
		assert self.shared_memory is None, 'cannot open shared mem twice'
		self.initialize_file()
		self.shared_memory = mmap.mmap(self.shared_handle, self.array_size, mmap.MAP_SHARED, mmap.PROT_WRITE)
		return self.shared_memory

class MMAPScreenReader(BaseMMapInterface, skyscreen.interface.ScreenReader):
	file_mode = os.O_RDONLY

	def __init__(self, shared_file):
		super(MMAPScreenReader, self).__init__(shared_file)

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


class SemaphoreWriterSync(skyscreen.interface.WriterSync):
	def __init__(self, sem):
		self.sem = sem
		assert sem.acquire(blocking=False),\
			'The semaphore must be acquire-able'
		sem.acquire()

	def frame_ready(self):
		self.sem.release()
		self.sem.acquire()

class SemaphoreReaderSync(skyscreen.interface.ReaderSync):
	def __init__(self, sem):
		self.sem = sem
		assert not sem.acquire(blocking=False), \
			'The semaphore should be acquired by the reader'
	def start_read(self):
		self.sem.acquire()

	def finish_read(self):
		self.sem.release()
