import cv2
import numpy as np

from skyscreen_core.interface import Screen
import skyscreen_core.interface as interface


n_screen_rows = Screen.screen_vane_count
n_screen_cols = Screen.screen_vane_count

output_location = None
window_size = 800
annulus = 50
paintable_area = interface.Screen.screen_max_magnitude*2+annulus*2

def make_mapping_matrix(v):
	rows = np.zeros((paintable_area, paintable_area))
	cols = np.zeros((paintable_area, paintable_area))

	for row in xrange(paintable_area):
		for col in xrange(paintable_area):
			rows[row, col] = (row - paintable_area/2) / 0.9
			cols[row, col] = (col - paintable_area/2) / 0.9
	mags, angles = cv2.cartToPolar(cols, rows)
	angles = np.round((angles / (2 * 3.141592) * 360)).astype(np.int32)
	mags = np.round(Screen.screen_max_magnitude - mags).astype(np.int32) + annulus
	return mags, angles

mags, angles = make_mapping_matrix(None)