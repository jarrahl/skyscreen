import logging


class Screen(object):
	"""
	The format for the screen_vane buffer is
    <--------- screen_vane_length ------->
	 CENTER ......................... EDGE
	+-------------------------------------+ ^
	|xxxxx RED CHANNEL, AT 0 degrees xxxxx| |
	|xxx GREEN CHANNEL, AT 0 degrees xxxxx| |
	|xxxxx BLUE CHANNEL, AT 0 degrees xxxx| |
	|xxxxx RED CHANNEL, AT 1 degrees xxxxx| |
	|xxx GREEN CHANNEL, AT 1 degrees xxxxx| |
	|xxxxx BLUE CHANNEL, AT 1 degrees xxxx| | screen_vane_count * 3
	|xxxxx RED CHANNEL, AT 2 degrees xxxxx| |
	|xxx GREEN CHANNEL, AT 2 degrees xxxxx| |
	|xxxxx BLUE CHANNEL, AT 2 degrees xxxx| |
	........AND SO ON IN THAT MANNER....... |
	|xxxx RED CHANNEL, AT 360 degrees xxxx| |
	|xx GREEN CHANNEL, AT 360 degrees xxxx| |
	|xxxx BLUE CHANNEL, AT 360 degrees xxx| |
	+-------------------------------------+ V
	"""
	screen_vane_length = 144 * 2
	screen_vane_count = 360
	array_size = screen_vane_count * screen_vane_length * 3

chanmap = {
	'r': 0,
	'g': 1,
	'b': 2
}

def pixel_vane_mapping(vane, pixel, channel):
	return vane * Screen.screen_vane_length * 3 + Screen.screen_vane_length * chanmap[channel] + pixel

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


class ScreenReader(Screen):
	def __enter__(self):
		"""
		:return: a ScreenBuffer
		"""
		raise NotImplementedError()

	def __exit__(self, type, value, traceback):
		raise NotImplementedError()

class WriterSync(object):
	def frame_ready(self):
		raise NotImplementedError()


class ReaderSync(object):
	def start_read(self):
		raise NotImplementedError()
	def finish_read(self):
		raise NotImplementedError()


class DummyWriterSync(WriterSync):
	def frame_ready(self):
		logging.warning('A dummy writer sync is being used, frame_ready calls do nothing')

class DummyReaderSync(WriterSync):
	def start_read(self):
		logging.warning('A dummy reader is being used, start_read calls do nothing')
	def finish_read(self):
		logging.warning('A dummy reader is being used, finish_read calls do nothing')

