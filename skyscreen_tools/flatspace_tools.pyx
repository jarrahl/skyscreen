from skyscreen_core import interface
from skyscreen_core.interface import Screen
cimport numpy as np
cimport cython
cdef extern from "math.h":
	double sin(double x)
	double round(double x)
	double tan(double x)
	double cos(double x)
	double sqrt(double x)
	double atan2(double x, double y)
	double pi
cdef int total_angles = Screen.screen_vane_count
cdef int total_mag = Screen.screen_max_magnitude

cdef int window_size, annulus, paintable_area;
window_size = 800
annulus = 50
paintable_area = interface.Screen.screen_max_magnitude*2+annulus*2

@cython.boundscheck(True)
def blit(np.ndarray[np.uint8_t, ndim = 3] input,
		 np.ndarray[np.uint8_t, ndim = 3] output,
		 np.ndarray[np.int32_t, ndim = 2] mags,
		 np.ndarray[np.int32_t, ndim = 2] angles):
	cdef int r, g, b
	cdef int row, col
	cdef int mag, angle
	for row in xrange(paintable_area):
		for col in xrange(paintable_area):
			mag = mags[row, col]
			angle = angles[row, col]
			if 0 <= mag < total_mag and 0 <= angle < total_angles:
				r = input[row, col, 0]
				g = input[row, col, 1]
				b = input[row, col, 2]
				output[angle, mag, 0] = r
				output[angle, mag, 1] = g
				output[angle, mag, 2] = b

