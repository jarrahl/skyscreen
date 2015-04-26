import logging
import os
import fcntl

class Screen(object):
	screen_vane_length = 144 * 2
	screen_rows = screen_vane_length
	screen_vane_count = 360
	screen_cols = screen_vane_count
	array_size = screen_vane_count * screen_vane_length * 3

chanmap = {
	'r': 0,
	'g': 1,
	'b': 2
}

def pixel_vane_mapping(vane, pixel, channel):
	return (vane * Screen.screen_vane_length * 3) + pixel * 3 + chanmap[channel]

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

	def frame_ready(self):
		raise NotImplementedError()


class ScreenReader(Screen):
	def __enter__(self):
		"""
		:return: a ScreenBuffer
		"""
		raise NotImplementedError()

	def __exit__(self, type, value, traceback):
		raise NotImplementedError()

	def start_read(self):
		raise NotImplementedError()

	def finish_read(self):
		raise NotImplementedError()


class WriterSync(object):
	def frame_ready(self):
		raise NotImplementedError()


class ReaderSync(object):
	def start_read(self):
		raise NotImplementedError()
	def finish_read(self):
		raise NotImplementedError()

class SemaphoreWriterSync(WriterSync):
	def __init__(self, sem):
		self.sem = sem
		assert sem.acquire(blocking=False), \
			'The semaphore must be acquire-able'
		sem.acquire()

	def frame_ready(self):
		self.sem.release()
		self.sem.acquire()

class SemaphoreReaderSync(ReaderSync):
	def __init__(self, sem):
		self.sem = sem
		assert not sem.acquire(blocking=False), \
			'The semaphore should be acquired by the reader'
	def start_read(self):
		self.sem.acquire()

	def finish_read(self):
		self.sem.release()


class DummyWriterSync(WriterSync):
	def frame_ready(self):
		logging.warning('A dummy writer sync is being used, frame_ready calls do nothing')

class DummyReaderSync(WriterSync):
	def start_reakd(self):
		logging.warning('A dummy reader is being used, start_read calls do nothing')
	def finish_read(self):
		logging.warning('A dummy reader is being used, finish_read calls do nothing')


class FlockWriterSync(WriterSync):
	def __init__(self, lock_file):
		self.lock_file = lock_file
		self.lock_handle = os.open(self.lock_file, os.O_RDONLY)
		logging.info("Locking file %s", self.lock_file)
		fcntl.flock(self.lock_handle, fcntl.LOCK_EX)
	
	def frame_ready(self):
		logging.info('Frame ready, unclocking %s', self.lock_file)
		fcntl.flock(self.lock_handle, fcntl.LOCK_UN)
		logging.info('re-locking %s', self.lock_file)
		fcntl.flock(self.lock_handle, fcntl.LOCK_EX)
		logging.info('Locked %s', self.lock_file)

import zmq

class ZMQWriterSync(WriterSync):
	def __init__(self, port=5555):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.socket.connect("tcp://127.0.0.1:%d" % port)

	def frame_ready(self):
		logging.info('Sending ready message')
		self.socket.send(b'ready')
		logging.info('Awaiting done message')
		self.socket.recv()
		logging.info('Finished')
