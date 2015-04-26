import numpy as np

import pyximport;
import time

from skyscreen_core.interface import Screen

pyximport.install()
import skyscreen_tools.flatspace
import skyscreen_tools.flatspace_tools


def test_polar_remap():
	test_input = np.zeros((Screen.screen_vane_count, Screen.screen_vane_count, 3), dtype=np.uint8)
	test_input[100, 100] = 255
	test_output = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length, 3), dtype=np.uint8)
	skyscreen_tools.flatspace_tools.polar_remap(test_input, test_output)


def test_remap_time():
	test_input = np.zeros((Screen.screen_vane_count, Screen.screen_vane_count, 3), dtype=np.uint8)
	test_input[100, 100] = 255
	test_output = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length, 3), dtype=np.uint8)
	start = time.time()
	n_frames = 100
	for i in range(n_frames):
		skyscreen_tools.flatspace_tools.polar_remap(test_input, test_output)
	end = time.time()
	assert end - start < 1, '%d frames took: %f, your system may not be fast enough' % (n_frames, end - start)


def test_coord_mapping():
	def test_fn(polar, cart):
		result = skyscreen_tools.flatspace_tools.polar_coord_transform(polar[0], polar[1])
		assert result == cart, \
			"polar coord %s was transformed to %s rather than %s" % (polar, result, cart)

	yield test_fn, (10, 0), (0, 10)
	yield test_fn, (10, 90), (10, 0)
	yield test_fn, (10, 180), (0, -10)
	yield test_fn, (10, 270), (-10, 0)

	yield test_fn, (100, 0), (0, 100)
	yield test_fn, (100, 90), (100, 0)
	yield test_fn, (100, 180), (0, -100)
	yield test_fn, (100, 270), (-100, 0)

	yield test_fn, (100, 45 + 0), \
		(np.round(1 / np.sqrt(2.0) * 100), np.round(1 / np.sqrt(2.0) * 100))
	yield test_fn, (10, 45 + 0), \
		  (np.round(1 / np.sqrt(2.0) * 10), np.round(1 / np.sqrt(2.0) * 10))
	# yield test_fn, (100, 45 + 90),  (100, 0)
	# yield test_fn, (100, 45 + 180), (0, -100)
	# yield test_fn, (100, 45 + 270), (-100, 0)