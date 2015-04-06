import logging
import os
import random
import sys
import argparse

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
						c = str(unichr(random.randint(0, 127)))
						offset = pixel_vane_mapping(vane, pixel, channel)
						writer_buf[offset] = c

def bands(writer):
	r = (str(unichr(127)), str(unichr(0)), str(unichr(0)))
	g = (str(unichr(0)), str(unichr(127)), str(unichr(0)))
	b = (str(unichr(0)), str(unichr(0)), str(unichr(127)))
	with writer as writer_buf:
		while True:
			print '.',; sys.stdout.flush()
			for vane in range(Screen.screen_vane_count):
				if vane % 3 == 0:
					for pixel in range(Screen.screen_vane_length):
						writer_buf[pixel_vane_mapping(vane, pixel, 'r')] = r[0]
						writer_buf[pixel_vane_mapping(vane, pixel, 'g')] = r[1]
						writer_buf[pixel_vane_mapping(vane, pixel, 'b')] = r[2]
				if vane % 3 == 1:
					for pixel in range(Screen.screen_vane_length):
						writer_buf[pixel_vane_mapping(vane, pixel, 'r')] = g[0]
						writer_buf[pixel_vane_mapping(vane, pixel, 'g')] = g[1]
						writer_buf[pixel_vane_mapping(vane, pixel, 'b')] = g[2]
				if vane % 3 == 2:
					for pixel in range(Screen.screen_vane_length):
						writer_buf[pixel_vane_mapping(vane, pixel, 'r')] = b[0]
						writer_buf[pixel_vane_mapping(vane, pixel, 'g')] = b[1]
						writer_buf[pixel_vane_mapping(vane, pixel, 'b')] = b[2]

def main():
	try:
		shared_file = os.environ['WRITER_FILE']
	except KeyError:
		print 'You must pass the shared file as WRITER_FILE env variable'
		sys.exit(1)

	parser = argparse.ArgumentParser(usage='name options: noise, bands')
	parser.add_argument('name', help='The name of the program to run')
	args = parser.parse_args()

	writer = skyscreen.mmap_interface.MMAPScreenWriter(shared_file)
	if args.name == 'noise':
		noise(writer)
	elif args.name == 'bands':
		bands(writer)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()