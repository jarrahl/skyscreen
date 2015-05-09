import skyscreen_core.interface as core


class ReshapingWriterWrapper(core.ScreenWriter):
	def __init__(self, writer):
		self.writer = writer

	def __enter__(self):
		self.buf = self.writer.__enter__()
		return self.buf.reshape((core.Screen.screen_vane_count, core.Screen.screen_max_magnitude, 3))

	def __exit__(self, type, value, traceback):
		del self.buf
		self.writer.__exit__(type, value, traceback)

	def frame_ready(self):
		self.writer.frame_ready()


class ReshapingWriterReader(core.ScreenReader):
	def __init__(self, reader):
		self.reader = reader
		self.buf = None

	def __enter__(self):
		self.buf = self.reader.__enter__()
		return self.buf.reshape((core.Screen.screen_vane_count, core.Screen.screen_max_magnitude, 3))

	def __exit__(self, type, value, traceback):
		del self.buf
		if hasattr(self.reader, '__exit__'):
			self.reader.__exit__(type, value, traceback)

	def start_read(self):
		self.reader.start_read()

	def finish_read(self):
		self.reader.finish_read()
