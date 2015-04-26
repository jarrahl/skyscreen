import numpy as np

import pyximport;
import time

from skyscreen_core.interface import Screen

pyximport.install()
import skyscreen_tools.flatspace


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
	n_frames = 1000
	for i in range(n_frames):
		skyscreen_tools.flatspace_tools.polar_remap(test_input, test_output)
	end = time.time()
	assert end - start < 1, '%d frames took: %f' % (n_frames, end - start)