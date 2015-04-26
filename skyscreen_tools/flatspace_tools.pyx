import math
from skyscreen_core.interface import Screen
cimport numpy as np
cimport cython
cdef extern from "math.h":
	double sin(double x)
	double round(double x)
	double cos(double x)
cdef int total_angles = Screen.screen_vane_count
cdef int total_mag = Screen.screen_vane_length

@cython.boundscheck(True)
def polar_remap(np.ndarray[np.uint8_t, ndim = 3] input, np.ndarray[np.uint8_t, ndim = 3] output):
	cdef int angle, mag
	cdef int col, row
	cdef int r, g, b
	for angle in xrange(total_angles):
		for mag in xrange(total_mag):
			row, col = c_polar_coord_transform(mag, angle)
			r = input[row, col, 0]
			output[angle, mag, 0] = r
			g = input[row, col, 1]
			output[angle, mag, 1] = g
			b = input[row, col, 2]
			output[angle, mag, 2] = b

# A wrapper for the c_polar_coord_transform below.
def polar_coord_transform(mag, angle):
	cdef int i_mag, i_angle
	i_angle = angle
	i_mag = mag
	return c_polar_coord_transform(i_mag, i_angle)

cdef (int, int)c_polar_coord_transform(int mag, int angle):
	cdef double d_angle, d_mag
	d_angle = <double>angle
	d_mag   = <double>mag
	row = <int>round(d_mag * sin(d_angle/360.0 * 2.0 * 3.14159265)) # Like Y
	col = <int>round(d_mag * cos(d_angle/360.0 * 2.0 * 3.14159265)) # Like X
	return row, col

