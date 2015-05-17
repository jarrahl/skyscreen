from collections import namedtuple

import logging
import os
import sys
import argparse
import subprocess
import signal

import bands
import noise
import test_patterns
import chaos
import video
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
	name = sys.argv[1]
	print sys.argv[2]
	print sys.argv[2]
	print sys.argv[2]
	print sys.argv[2]
	print sys.argv[2]
	print sys.argv[2]
	print sys.argv[2]
	run_named(name)

name_fn_map = {
	'noise': lambda writer: noise.noise(writer),
	'bands': lambda writer: bands.bands(writer),
	'npnoise': lambda writer: noise.numpy_random(writer),
	'theano.swirl': lambda writer: theano_examples.theano_swirl(writer),
	'theano.tripdar': lambda writer:  theano_examples.theano_tripdar(writer),
	'theano.radar': lambda writer:  theano_examples.theano_radar(writer),
	'theano.droplet': lambda writer:  theano_examples.theano_droplet(writer),
	'chaos': lambda writer:  chaos.chaos(writer),
	'fsm.random_game': lambda writer:  fsm.game_of_life(writer, sub_prog='random'),
	'fsm.gliders': lambda writer:  fsm.game_of_life(writer, sub_prog='gliders'),
	'test.lines': lambda writer:  test_patterns.simple_lines(writer),
	'test.grid': lambda writer:  test_patterns.grid(writer),
	'video': lambda writer:  video.video(writer, sys.argv[2]),
}

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

	if name in name_fn_map:
		name_fn_map[name](writer)
	else:
		logging.error('Unknown name "%s"', name)
		sys.exit(1)
