"""
Here are some simple example screens. Nothing too fancy.
"""

import logging
import os
import sys
import argparse

import bands
import noise
import theano_examples
import skyscreen_core.memmap_interface


TARGET_FPS=25


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
		noise.noise(writer)
	elif args.name == 'bands':
		bands.bands(writer)
	elif args.name == 'npnoise':
		noise.numpy_random(writer)
	elif args.name == 'theano.scan':
		theano_examples.theano_scan(writer)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()