import logging
import os
import random
import sys
import argparse
import time

import numpy as np

from skyscreen_core.interface import Screen, pixel_vane_mapping
import skyscreen_core.memmap_interface
import skyscreen_core.mmap_interface

TARGET_FPS=25

def theano_scan(writer):
	try:
		import theano
		import theano.tensor as T
	except ImportError:
		logging.error("Theano not found, exiting")
		sys.exit(1)
	else:
		logging.warning("You're using theano! Nice! You may want to look into the runtime flags")

	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		vane_matrix = [[[vane, vane, vane] for px in range(Screen.screen_vane_length)]
					   for vane in range(Screen.screen_vane_count)]
		px_matrix =   [[[px,px*2,px*3] for px in range(Screen.screen_vane_length)]
					   for vane in range(Screen.screen_vane_count)]
		vane_vec = T.as_tensor(vane_matrix)
		px_vec = T.as_tensor(px_matrix)
		step = T.fscalar('step')

		def draw(vane, px):
			return 255*T.sin((vane+px+step)/25.0)

		f, _ = theano.map(draw, [vane_vec, px_vec])

		fn_actual = theano.function([step], f, allow_input_downcast=True)

		step_actual = 0
		while True:
			start = time.time()
			writer_buf_reshaped[:] = fn_actual(step_actual)
			step_actual -= 1
			done = time.time()
			fps = 1.0/(done - start)
			if (fps < TARGET_FPS):
				logging.warning('Frame rate is %f, which is lower than target %d', fps, TARGET_FPS)




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

	writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(shared_file)
	if args.name == 'noise':
		noise(writer)
	elif args.name == 'bands':
		bands(writer)
	elif args.name == 'npnoise':
		numpy_random(writer)
	elif args.name == 'theano.scan':
		theano_scan(writer)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()