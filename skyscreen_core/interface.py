# coding=utf-8
import logging
import os
import fcntl


class Screen(object):
	"""
	General bits and pieces that define how the screen fits together.

	- screen_max_magnitude - the length of a screen arm, in terms of LEDs
	- screen_cols - the same as screen_max_magnitude
	- screen_vane_count - the angular resolution, ie, there are this many separate arm positions.
	- screen_rows - the same as screen_vane_count
	- array size - because we represent the screen as an array, this is its total size.

	Array Format
	============

	The skyscreen array looks like this in memory ::

		        0                   screen_max_magnitude
		        ┌─────────────────────────────────────┐   0
		inside  │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│ outside
		of      │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│  of
		screen                 ...                      screen
		                       ...
		        │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│
		        └─────────────────────────────────────┘ screen_vane_count

	:func:`pixel_vane_mapping` defines the exact pixel to offset mapping

	"""
	screen_max_magnitude = 288
	screen_cols = screen_max_magnitude
	screen_vane_count = 360
	screen_rows = screen_vane_count
	array_size = screen_vane_count * screen_max_magnitude * 3


chanmap = {
	'r': 0,
	'g': 1,
	'b': 2
}


def pixel_vane_mapping(vane, pixel, channel):
	"""
	Gives the offset of a pixel::

		(vane * Screen.screen_max_magnitude * 3) + pixel * 3 + chanmap[channel]
	"""
	return (vane * Screen.screen_max_magnitude * 3) + pixel * 3 + chanmap[channel]


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
	"""
	A screen reader. Its enter method should return a buffer.

	The start_read() call should be called BEFORE reading from the buffer.
	It will block until the frame has been fully written. The finish_read()
	function should be called as soon as possible, once the frame has been
	handled, to signal that it is safe for the writer to start editing the
	frame again. HOWEVER this role may also be undertaken by start_read() as
	well, so make your processing fast!

	The __exit__() method MUST clean up after itself, regardless of the call
	status of start_read() and finish_read().
	"""
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
	def __init__(self):
		logging.warning('A dummy WriterSync is being used. Sync calls do nothing')

	def frame_ready(self):
		pass


class DummyReaderSync(WriterSync):
	def __init__(self):
		logging.warning('A dummy WriterSync is being used. Sync calls do nothing')

	def start_read(self):
		pass

	def finish_read(self):
		pass


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


class ZMQReaderSync(ReaderSync):
	def __init__(self, port=5555):
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://127.0.0.1:%d" % port)

	def start_read(self):
		self.socket.recv()

	def finish_read(self):
		self.socket.send('Done')
