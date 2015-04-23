import numpy as np
import scipy.ndimage.filters as filters
from skyscreen_core.interface import Screen


def rps(writer, lock):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		convolution_mat = np.array([
			[1, 0, 1],
			[0, 0, 0],
			[1, 0, 1],
		]) / 8.0

		r_score = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length))
		g_score = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length))
		b_score = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length))
		r_score[:, 23] = 1.0
		g_score[33, :] = 1.0
		b_score[:, 99] = 1.0

		while True:
			lock.frame_ready()

			r_score += filters.convolve(r_score, convolution_mat)
			print np.sum(r_score)

			writer_buf_reshaped[:, :, 0] = 255 * r_score
			writer_buf_reshaped[:, :, 1] = 255 * g_score
			writer_buf_reshaped[:, :, 2] = 255 * b_score

