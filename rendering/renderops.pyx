import math
import numpy as np

from cpython cimport array as c_array
from array import array

cdef c_array.array a = array('i', [1, 2, 3])

pi = 3.1415926
screen_vane_length = 144*2
screen_vane_count = 360
window_size = 800
shrinkage_factor = 0.9
annulus_offset = 50


def calculate_theta(vane):
	return 2 * pi * float(vane) / screen_vane_count


def calculate_radius(pixel):
	pixel_proportion = float(pixel) / screen_vane_length
	render_area_size = (window_size / 2 * shrinkage_factor) - annulus_offset
	return annulus_offset + render_area_size * pixel_proportion


def polar_coordinate_transform(theta, radius):
	center = window_size / 2.0
	x = center + radius * np.cos(theta)
	y = center + radius * np.sin(theta)
	return int(x), int(y)


chanmap = {
	'r': 0,
	'g': 1,
	'b': 2
}

def pixel_vane_mapping(vane, pixel, channel):
	return (vane * screen_vane_length * 3) + pixel * 3 + chanmap[channel]


def render_buffer(surf, reader_buf):
	vane = 0
	while vane < screen_vane_count:
		theta = calculate_theta(vane)
		pixel = 0
		while pixel < screen_vane_length:
			radius = calculate_radius(pixel)
			x, y = polar_coordinate_transform(theta, radius)
			r = reader_buf[pixel_vane_mapping(vane, pixel, 'r')]
			g = reader_buf[pixel_vane_mapping(vane, pixel, 'g')]
			b = reader_buf[pixel_vane_mapping(vane, pixel, 'b')]

			surf[x][y] = [r, g, b]
			surf[x + 1][y] = [r, g, b]
			surf[x - 1][y] = [r, g, b]
			surf[x][y + 1] = [r, g, b]
			surf[x][y - 1] = [r, g, b]
			pixel += 1
		vane += 1