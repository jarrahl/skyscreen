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
from patterns import chaos
import patterns.test_patterns
import theano_examples
import fsm
import skyscreen_core.memmap_interface
import skyscreen_core.interface


TARGET_FPS = 25


def run_displayimage(shared_path, python_proc, use_old_display=False):
	new_env = dict(os.environ.items())
	new_env['WRITER_FILE'] = shared_path
	new_env['LOCK_METHOD'] = 'zmq'
	if use_old_display:
		display = subprocess.Popen('rendering/DisplayImage', env=new_env)
	else:
		display = subprocess.Popen(['python', 'pyrendering/render.py', shared_path], env=new_env)
	display.wait()
	os.kill(python_proc, signal.SIGKILL)
	os.waitpid(python_proc, 0)


def main():
	parser = argparse.ArgumentParser(usage='name options: noise, bands')
	parser.add_argument('name', help='The name of the program to run')
	args = parser.parse_args()
	name = args.name

	run_named(name)


def run_named(name, use_old_display=False):
	# shared_file = tempfile.NamedTemporaryFile()
	SF = namedtuple('SF', ['name'])
	shared_file = SF(name='rendering/foo')

	pid = os.fork()
	if pid != 0:
		run_displayimage(shared_file.name, pid, use_old_display)
		return
	# lock = skyscreen_core.interface.FlockWriterSync(shared_file.name)
	# lock = skyscreen_core.interface.DummyWriterSync()
	lock = skyscreen_core.interface.ZMQWriterSync()
	writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(shared_file.name, lock)

	if name == 'noise':
		noise.noise(writer)
	elif name == 'bands':
		bands.bands(writer)
	elif name == 'npnoise':
		noise.numpy_random(writer)
	elif name == 'theano.swirl':
		theano_examples.theano_swirl(writer)
	elif name == 'theano.tripdar':
		theano_examples.theano_tripdar(writer)
	elif name == 'theano.radar':
		theano_examples.theano_radar(writer)
	elif name == 'theano.droplet':
		theano_examples.theano_droplet(writer)
	elif name == 'chaos':
		chaos.chaos(writer)
	elif name == 'fsm.rps':
		fsm.rps(writer)
	elif name == 'fsm.random_game':
		fsm.game_of_life(writer, sub_prog='random')
	elif name == 'fsm.gliders':
		fsm.game_of_life(writer, sub_prog='gliders')
	elif name == 'test.lines':
		patterns.test_patterns.simple_lines(writer)
	elif name == 'test.grid':
		patterns.test_patterns.grid(writer)
	else:
		logging.error('Unknown name "%s"', name)
		sys.exit(1)
