import logging
import os
import random
import sys
import argparse
import numpy as np
import time

from skyscreen.interface import Screen, pixel_vane_mapping
import skyscreen.memmap_interface
import skyscreen.mmap_interface


def noise(writer):
	with writer as writer_buf:
		while True:
			print '.',; sys.stdout.flush()
			for vane in xrange(Screen.screen_vane_count):
				for pixel in xrange(Screen.screen_vane_length):
					for channel in {'r', 'g', 'b'}:
						c = random.randint(0, 255)
						offset = pixel_vane_mapping(vane, pixel, channel)
						writer_buf[offset] = c

def bands(writer):
	r = (255, 0, 0)
	g = (0, 255, 0)
	b = (0, 0, 255)
	band_matrix = np.zeros(shape=(Screen.screen_vane_count, Screen.screen_vane_length, 3))

	count = 0

	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		while True:
			for band in xrange(Screen.screen_vane_count):
				band_matrix[band, :, 0] = 255 * (band % 3 == ((count + 0) % 3))
				band_matrix[band, :, 1] = 255 * (band % 3 == ((count + 1) % 3))
				band_matrix[band, :, 2] = 255 * (band % 3 == ((count + 2) % 3))
				writer_buf_reshaped[:] = band_matrix
			count += 1
			print '.',; sys.stdout.flush()

def numpy_random(writer):
	with writer as writer_buf:
		while True:
			writer_buf[:] = 255*np.random.random(size=writer_buf.shape)
			writer_buf.flush()


def main():
	try:
		shared_file = os.environ['WRITER_FILE']
	except KeyError:
		print 'You must pass the shared file as WRITER_FILE env variable'
		sys.exit(1)

	parser = argparse.ArgumentParser(usage='name options: noise, bands')
	parser.add_argument('name', help='The name of the program to run')
	args = parser.parse_args()

	writer = skyscreen.memmap_interface.NPMMAPScreenWriter(shared_file)
	if args.name == 'noise':
		noise(writer)
	elif args.name == 'bands':
		bands(writer)
	elif args.name == 'npnoise':
		numpy_random(writer)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()