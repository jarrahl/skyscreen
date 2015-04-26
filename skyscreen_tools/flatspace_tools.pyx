import math
from skyscreen_core.interface import Screen
cimport numpy as np
cimport cython
cdef extern from "math.h":
	double sin(double x)
	double cos(double x)
cdef int total_angles = Screen.screen_vane_count
cdef int total_mag = Screen.screen_vane_length

@cython.boundscheck(False)
def polar_remap(np.ndarray[np.uint8_t, ndim = 3] input, np.ndarray[np.uint8_t, ndim = 3] output):
	cdef int angle, mag
	cdef double d_angle, d_mag
	cdef int col, row
	cdef double d_col, d_row
	for angle in xrange(total_angles):
		for mag in xrange(total_mag):
			d_angle = <double>angle
			d_mag   = <double>mag
			col = <int>(d_mag * sin(d_angle/360.0 * 2.0 * 3.14159265))
			row = <int>(d_mag * cos(d_angle/360.0 * 2.0 * 3.14159265))

			output[angle, mag, 0] = input[row, col, 0]
			output[angle, mag, 1] = input[row, col, 1]
			output[angle, mag, 2] = input[row, col, 2]