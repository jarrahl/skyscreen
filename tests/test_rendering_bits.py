import logging
import math
import random
import tempfile
import skyscreen.mmap_interface
import skyscreen.memmap_interface
from skyscreen.interface import Screen, WriterSync, ReaderSync, pixel_vane_mapping
import pyximport
pyximport.install()
import skyscreen.rendering as rendering
import skyscreen.rendering.renderops as renderops


def test_theta_calc():
	degrees = [renderops.calculate_theta(degree) for degree in xrange(Screen.screen_vane_count)]
	assert sorted(degrees) == degrees
	assert min(degrees) == 0
	assert 2 * math.pi * 0.99 <= max(degrees) <= 2 * math.pi
	deltas = {a - b for a, b in zip(degrees, degrees[1:])}
	assert max(deltas) - min(deltas) < 0.01


def test_calculate_radius():
	positions = [renderops.calculate_radius(pixel) for pixel in xrange(Screen.screen_vane_length)]
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
				assert position < Screen.array_size, '%d was out of range %d (%d, %d, %s)' % \
													 (position, Screen.array_size, vane, pixel, channel)

def render(generate_callback):
	filename = tempfile.mktemp("")
	writer = skyscreen.memmap_interface.NPMMAPScreenWriter(filename)
	writer.initialize_file()
	reader = skyscreen.memmap_interface.NPMMAPScreenReader(filename)
	sync = skyscreen.interface.DummyReaderSync()

	callback = generate_callback(writer)

	with reader as reader_buf:
		rendering.render_main(reader_buf, sync, max_loops=5, callback=callback)

def test_noise():
	def generate_write_random(writer):
		def inner():
			with writer as writer_buf:
				for offset in range(len(writer_buf)):
					c = random.randint(0, 255)
					writer_buf[offset] = c
		return inner
	render(generate_write_random)

def test_stripes():
	def generate_write_random_stripes(writer):
		def inner():
			with writer as writer_buf:
				for vane in range(Screen.screen_vane_count):
					r = ((vane % 3) == 0) * 255
					g = ((vane % 3 - 1) == 0) * 255
					b = ((vane % 3 - 2) == 0) * 255
					for pixel in range(Screen.screen_vane_length):
						writer_buf[rendering.pixel_vane_mapping(vane, pixel, 'r')] = r
						writer_buf[rendering.pixel_vane_mapping(vane, pixel, 'g')] = g
						writer_buf[rendering.pixel_vane_mapping(vane, pixel, 'b')] = b
		return inner

	render(generate_write_random_stripes)
