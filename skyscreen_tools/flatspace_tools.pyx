from skyscreen_core import interface
from skyscreen_core.interface import Screen
import skyscreen_tools.flatspace_const
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


# Pull these in from the globals and make sure they're the
# right datatype. For a _tiny_ speed advantage
cdef np.int32_t[:, :] mags, angles;
mags = skyscreen_tools.flatspace_const.mags
angles = skyscreen_tools.flatspace_const.angles

@cython.boundscheck(False)
def blit_polar(
		np.ndarray[np.uint8_t, ndim = 3] input,
		np.ndarray[np.uint8_t, ndim = 3] output):
	cdef int r, g, b
	cdef int row, col
	cdef int mag, angle
	global mags, angles
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

@cython.boundscheck(True)
def blit_mapping(
		np.ndarray[np.uint8_t, ndim = 3] input,
	 	np.ndarray[np.uint8_t, ndim = 3] output,
		np.ndarray[np.int32_t, ndim = 2] mag_map,
		np.ndarray[np.int32_t, ndim = 2] angle_map):
	cdef int r, g, b
	cdef int row, col
	cdef int mag, angle
	global mags, angles
	for row in xrange(paintable_area):
		for col in xrange(paintable_area):
			mag = mag_map[row, col]
			angle = angle_map[row, col]
			if 0 <= mag < total_mag and 0 <= angle < total_angles:
				r = input[row, col, 0]
				g = input[row, col, 1]
				b = input[row, col, 2]
				output[angle, mag, 0] = r
				output[angle, mag, 1] = g
				output[angle, mag, 2] = b