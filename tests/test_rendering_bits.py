import logging
import math
import random
import tempfile
import skyscreen.mmap_interface
from skyscreen.interface import Screen, WriterSync, ReaderSync, pixel_vane_mapping
import skyscreen.rendering as rendering

def test_theta_calc():
	degrees = [rendering.calculate_theta(degree) for degree in xrange(Screen.screen_vane_count)]
	assert sorted(degrees) == degrees
	assert min(degrees) == 0
	assert 2 * math.pi * 0.99 <= max(degrees) <= 2 * math.pi
	deltas = {a - b for a, b in zip(degrees, degrees[1:])}
	assert max(deltas) - min(deltas) < 0.01

def test_calculate_radius():
	positions = [rendering.calculate_radius(pixel) for pixel in xrange(Screen.screen_vane_length)]
	assert sorted(positions) == positions
	assert min(positions) == rendering.annulus_offset
	assert (rendering.shrinkage_factor - 0.01) * (rendering.window_size / 2.0) <= \
		   max(positions) <= \
		   (rendering.shrinkage_factor + 0.01) * (rendering.window_size / 2.0)
	deltas = {a - b for a, b in zip(positions, positions[1:])}
	assert max(deltas) - min(deltas) < 0.01

def test_position_overflows():
	for vane in xrange(Screen.screen_vane_count):
		for pixel in xrange(Screen.screen_vane_length):
			for channel in {'r', 'g', 'b'}:
				position = rendering.pixel_vane_mapping(vane, pixel, channel)
				assert position < Screen.array_size, '%d was out of range %d (%d, %d, %s)' %\
													 (position, Screen.array_size, vane, pixel, channel)

def _test_noise():
	filename = tempfile.mktemp("")
	writer = skyscreen.mmap_interface.MMAPScreenWriter(filename)
	reader = skyscreen.mmap_interface.MMAPScreenReader(filename)
	sync = skyscreen.interface.DummyReaderSync()

	with writer as writer_buf:
		for offset in range(len(writer_buf)):
			c = str(unichr(random.randint(0, 127)))
			writer_buf[offset] = c

	with reader as reader_buf:
		rendering.render_main(reader_buf, sync)

def _test_red():
	filename = tempfile.mktemp("")
	writer = skyscreen.mmap_interface.MMAPScreenWriter(filename)
	reader = skyscreen.mmap_interface.MMAPScreenReader(filename)
	sync = skyscreen.interface.DummyReaderSync()

	with writer as writer_buf:
		for vane in xrange(Screen.screen_vane_count):
			for pixel in xrange(Screen.screen_vane_length):
				for channel in {'r', 'g', 'b'}:
					if channel == 'r':
						c = str(unichr(random.randint(0, 127)))
					else:
						c = '\0'
					offset = pixel_vane_mapping(vane, pixel, channel)
					writer_buf[offset] = c

	with reader as reader_buf:
		rendering.render_main(reader_buf, sync)
