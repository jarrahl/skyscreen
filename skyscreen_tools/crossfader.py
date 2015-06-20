"""
A simple crossfading mixer module.

This takes TWO input readers, and then cross fades them, forming a writer
"""
import skyscreen_core.interface


class CrossFaderFromReaders(object):
	def __init__(self,
				 reader_left,
				 reader_right,
				 output_writer):
		assert isinstance(reader_left, skyscreen_core.interface.ScreenReader)
		assert isinstance(reader_right, skyscreen_core.interface.ScreenReader)
		assert isinstance(output_writer, skyscreen_core.interface.ScreenWriter)
		self.reader_left = reader_left
		self.reader_right = reader_right
		self.output_writer = output_writer

	def __enter__(self):
		with self.output_writer as output, \
				self.reader_left as left, \
				self.reader_right as right:
			self.output = output
			self.left = left
			self.right = right

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.reader_right.__exit__(exc_type, exc_val, exc_tb)
		self.reader_left.__exit__(exc_type, exc_val, exc_tb)
		self.output_writer.__exit__(exc_type, exc_val, exc_tb)

	def step(self, mixing_level):
		self.reader_left.start_read()
		self.reader_right.start_read()
		self.output[:] = self.left * mixing_level + self.right * (1 - mixing_level)
		self.reader_left.finish_read()
		self.reader_right.finish_read()
		self.output_writer.frame_ready()