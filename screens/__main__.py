"""
Here are some simple example screens. Nothing too fancy.
"""
from collections import namedtuple

import logging
import os
import sys
import argparse
import tempfile
import subprocess
import signal

import bands
import noise
from screens import chaos
import screens.simple_lines
import theano_examples
import fsm
import skyscreen_core.memmap_interface
import skyscreen_core.interface


TARGET_FPS=25

def run_displayimage(shared_path, python_proc):
	new_env = dict(os.environ.items())
	new_env['WRITER_FILE'] = shared_path
	new_env['LOCK_METHOD'] = 'zmq'
	#display = subprocess.Popen('rendering/DisplayImage', env=new_env)
	display = subprocess.Popen(['python', 'pyrendering/render.py', shared_path], env=new_env)
	display.wait()
	os.kill(python_proc, signal.SIGKILL)
	os.waitpid(python_proc, 0)

def main():
	#shared_file = tempfile.NamedTemporaryFile()
	SF = namedtuple('SF', ['name'])
	shared_file = SF(name='rendering/foo')

	parser = argparse.ArgumentParser(usage='name options: noise, bands')
	parser.add_argument('name', help='The name of the program to run')
	args = parser.parse_args()

	pid = os.fork()
	if pid != 0:
		run_displayimage(shared_file.name, pid)
		exit(0)
	#lock = skyscreen_core.interface.FlockWriterSync(shared_file.name)
	#lock = skyscreen_core.interface.DummyWriterSync()
	lock = skyscreen_core.interface.ZMQWriterSync()
	writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(shared_file.name, lock)

	if args.name == 'noise':
		noise.noise(writer)
	elif args.name == 'bands':
		bands.bands(writer)
	elif args.name == 'npnoise':
		noise.numpy_random(writer)
	elif args.name == 'theano.swirl':
		theano_examples.theano_swirl(writer)
	elif args.name == 'theano.tripdar':
		theano_examples.theano_tripdar(writer)
	elif args.name == 'theano.radar':
		theano_examples.theano_radar(writer)
	elif args.name == 'theano.droplet':
		theano_examples.theano_droplet(writer)
	elif args.name == 'chaos':
		chaos.chaos(writer)
	elif args.name == 'fsm.rps':
		fsm.rps(writer)
	elif args.name == 'fsm.random_game':
		fsm.game_of_life(writer, sub_prog='random')
	elif args.name == 'fsm.gliders':
		fsm.game_of_life(writer, sub_prog='gliders')
	elif args.name == 'lines':
		screens.simple_lines.simple_lines(writer)
	else:
		logging.error('Unknown name "%s"', args.name)
		sys.exit(1)

if __name__=='__main__':
	main()
