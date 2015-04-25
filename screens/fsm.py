import numpy as np
import scipy.ndimage.filters as filters
import time
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


def game_of_life_channel(gol_arr):
	right = np.roll(gol_arr, 1)
	left = np.roll(gol_arr, -1)
	down = np.roll(gol_arr, 1, axis=0)
	up = np.roll(gol_arr, -1, axis=0)
	upright = np.roll(left, 1, axis=0)
	upleft = np.roll(left, -1, axis=0)
	downright = np.roll(right, 1, axis=0)
	downleft = np.roll(right, -1, axis=0)

	px_sums = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=np.byte)
	px_sums += down
	px_sums += up
	px_sums += left
	px_sums += right
	px_sums += upright
	px_sums += upleft
	px_sums += downright
	px_sums += downleft
	px_sums += gol_arr
	#import debug

	gol_arr[px_sums == 3] = True
	gol_arr[px_sums < 3] = False
	gol_arr[px_sums > 4] = False


def game_of_life(writer, lock):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))


		gol_arr_r = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=bool)
		gol_arr_g = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=bool)
		gol_arr_b = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=bool)
		gol_arr_r[:] = np.round(
			abs(np.random.random((Screen.screen_vane_count, Screen.screen_vane_length)) - 0.3)
		)
		gol_arr_g[:] = np.round(
			abs(np.random.random((Screen.screen_vane_count, Screen.screen_vane_length)) - 0.3)
		)
		gol_arr_b[:] = np.round(
			abs(np.random.random((Screen.screen_vane_count, Screen.screen_vane_length)) - 0.3)
		)
		for i in range(0, 100, 5):
			gol_arr_r[i+0, i+1] = True
			gol_arr_r[i+1, i+2] = True
			gol_arr_r[i+2, i+0] = True
			gol_arr_r[i+2, i+1] = True
			gol_arr_r[i+2, i+2] = True

			gol_arr_r[i+1+10, i+0] = True
			gol_arr_r[i+2+10, i+1] = True
			gol_arr_r[i+0+10, i+2] = True
			gol_arr_r[i+1+10, i+2] = True
			gol_arr_r[i+2+10, i+2] = True


			gol_arr_r[i-1+144, i+0] = True
			gol_arr_r[i-2+144, i+1] = True
			gol_arr_r[i-0+144, i+2] = True
			gol_arr_r[i-1+144, i+2] = True
			gol_arr_r[i-2+144, i+2] = True

		while True:
			game_of_life_channel(gol_arr_r)
			game_of_life_channel(gol_arr_g)
			game_of_life_channel(gol_arr_b)
			writer_buf_reshaped[:, :, 0] += gol_arr_r % 255
			writer_buf_reshaped[:, :, 1] += gol_arr_g % 255
			writer_buf_reshaped[:, :, 2] += gol_arr_b % 255
			lock.frame_ready()
