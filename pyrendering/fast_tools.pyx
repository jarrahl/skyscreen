import skyscreen_core.interface
cimport numpy as np
cimport cython

cdef int screen_max_angle = skyscreen_core.interface.Screen.screen_vane_count
cdef int screen_max_magnitude = skyscreen_core.interface.Screen.screen_max_magnitude

@cython.boundscheck(True)
def quickblit(np.ndarray[np.uint8_t, ndim = 3] input_arr,
			  np.ndarray[np.uint8_t, ndim = 3] output_arr,
			  np.ndarray[np.int32_t, ndim = 2] row_mapping,
			  np.ndarray[np.int32_t, ndim = 2] col_mapping):
	"""
	Blit data rapidly from input_arr to output_arr, via a mapping. The mapping
	is in row_mapping and col_mapping. The mapping algorithm is: ::
		rt = row_mapping[r, c]
		ct = col_mapping[r, c]
		outut_array[rt, ct] = input_array[r, c]

	However, it will also:
	 - fill out the points a little more by also adding to the pixels around it
	 - and it'll do the blit for all channels.


	:param input_arr: the input array
	:type input_arr: a numpy array, with 3 dimensions and with type uint8
	:param output_arr: the output array
	:type output_arr: a numpy array, with 3 dimensions and with type uint8
	:param row_mapping: the row mappings
	:type row_mapping: a numpy array, with 2 dimensions and with type int32
	:param col_mapping: the col mappings
	:type col_mapping: a numpy array, with 2 dimensions and with type int32
	"""
	cdef int row, col, chan
	for angle in range(screen_max_angle):
		for mag in range(screen_max_magnitude):
			row = row_mapping[angle, mag]
			col = col_mapping[angle, mag]

			chan = 0
			output_arr[row, col,   chan] = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col+1, chan] = input_arr[angle, mag, chan]
			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]

			chan = 1
			output_arr[row, col,   chan] = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col+1, chan] = input_arr[angle, mag, chan]
			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]

			chan = 2
			output_arr[row, col,   chan] = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col+1, chan] = input_arr[angle, mag, chan]
			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]
