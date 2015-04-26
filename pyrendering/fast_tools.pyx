import skyscreen_core.interface
cimport numpy as np
cimport cython

cdef int screen_max_angle = skyscreen_core.interface.Screen.screen_vane_count
cdef int screen_max_magnitude = skyscreen_core.interface.Screen.screen_vane_length

@cython.boundscheck(False)
def quickblit(np.ndarray[np.uint8_t, ndim = 3] input_arr,
			  np.ndarray[np.uint8_t, ndim = 3] output_arr,
			  np.ndarray[np.int32_t, ndim = 2] row_mapping,
			  np.ndarray[np.int32_t, ndim = 2] col_mapping):
	cdef int row, col, chan
	for angle in range(screen_max_angle):
		for mag in range(screen_max_magnitude):
			row = row_mapping[angle, mag]
			col = col_mapping[angle, mag]
			chan = 0
			output_arr[row, col, chan]   = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col+1, chan] = input_arr[angle, mag, chan]
			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]
			chan = 1
			output_arr[row, col, chan]   = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]


			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]
			chan = 2
			output_arr[row, col, chan]   = input_arr[angle, mag, chan]
			output_arr[row+1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col+1, chan] = input_arr[angle, mag, chan]
			output_arr[row-1, col, chan] = input_arr[angle, mag, chan]
			output_arr[row, col-1, chan] = input_arr[angle, mag, chan]
