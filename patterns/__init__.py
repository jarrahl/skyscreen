import sys

import bands
import noise
import test_patterns
import chaos
import video
import theano_examples
import fsm


TARGET_FPS = 25





name_fn_map = {
	'noise': lambda writer: noise.noise(writer),
	'bands': lambda writer: bands.bands(writer),
	'npnoise': lambda writer: noise.numpy_random(writer),
	'theano.swirl': lambda writer: theano_examples.theano_swirl(writer),
	'theano.tripdar': lambda writer: theano_examples.theano_tripdar(writer),
	'theano.radar': lambda writer: theano_examples.theano_radar(writer),
	'theano.droplet': lambda writer: theano_examples.theano_droplet(writer),
	'chaos': lambda writer: chaos.chaos(writer),
	'fsm.random_game': lambda writer: fsm.game_of_life(writer, sub_prog='random'),
	'fsm.gliders': lambda writer: fsm.game_of_life(writer, sub_prog='gliders'),
	'test.lines': lambda writer: test_patterns.simple_lines(writer),
	'test.grid': lambda writer: test_patterns.grid(writer),
	'video': lambda writer: video.video(writer, sys.argv[2]),
}


