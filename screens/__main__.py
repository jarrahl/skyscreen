import logging
import os
import random
import sys
from skyscreen.interface import Screen, pixel_vane_mapping
import skyscreen.mmap_interface

try:
	shared_file = os.environ['WRITER_FILE']
except KeyError:
	print 'You must pass the shared file as WRITER_FILE env variable'
	sys.exit(1)

writer = skyscreen.mmap_interface.MMAPScreenWriter(shared_file)
while True:
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
	logging.warning('Written a screen')