"""
Here are some simple example screens. Nothing too fancy.
"""

import logging
import os
import sys
import argparse

import bands
import noise
from screens import chaos
import theano_examples
import fsm
import skyscreen_core.memmap_interface
import skyscreen_core.interface


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
	lock = skyscreen_core.interface.FlockWriterSync(shared_file)
	#lock = skyscreen_core.interface.DummyWriterSync()
	if args.name == 'noise':
		noise.noise(writer, lock)
	elif args.name == 'bands':
		bands.bands(writer, lock)
	elif args.name == 'npnoise':
		noise.numpy_random(writer, lock)
	elif args.name == 'theano.swirl':
		theano_examples.theano_swirl(writer, lock)
	elif args.name == 'theano.tripdar':
		theano_examples.theano_tripdar(writer, lock)
	elif args.name == 'theano.radar':
		theano_examples.theano_radar(writer, lock)
	elif args.name == 'theano.droplet':
		theano_examples.theano_droplet(writer, lock)
	elif args.name == 'chaos':
		chaos.chaos(writer, lock)
	elif args.name == 'fsm.rps':
		fsm.rps(writer, lock)
	elif args.name == 'fsm.gol':
		fsm.game_of_life(writer, lock)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()
