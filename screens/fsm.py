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


def game_of_life(writer, lock):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))


		gol_arr = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=bool)
		# gol_arr[:] = np.round(
		# 	abs(np.random.random((Screen.screen_vane_count, Screen.screen_vane_length)) - 0.3)
		# )
		gol_arr[144, 144] = True
		gol_arr[143, 144] = True
		gol_arr[142, 144] = True
		gol_arr[142, 145] = True
		gol_arr[142, 146] = True
		gol_arr[143, 147] = True

		while True:
			lock.frame_ready()
			print "."
			writer_buf_reshaped[:, :, 0] = gol_arr * 255
			writer_buf_reshaped[:, :, 1] = gol_arr * 255
			writer_buf_reshaped[:, :, 2] = gol_arr * 255

			#for angle in xrange(1, Screen.screen_vane_count - 1):
			#	for mag in xrange(1, Screen.screen_vane_length - 1):
			#		px_sum = 0
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle+1, mag  ])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle-1, mag  ])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle+1, mag+1])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle,   mag+1])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle-1, mag+1])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle+1, mag-1])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle,   mag-1])
			#		px_sum += (gol_arr[angle, mag] == gol_arr[angle-1, mag-1])
#
			#		if px_sum == 3:
			#			gol_arr[angle, mag] = True
			#		elif px_sum == 4:
			#			gol_arr[angle, mag] = not gol_arr[angle, mag]
			#		else:
			#			gol_arr[angle, mag] = False
			b = np.roll(gol_arr, 1)
			t = np.roll(gol_arr, -1)
			l = np.roll(gol_arr, 1, axis=1)
			r = np.roll(gol_arr, -1, axis=1)
			tl = np.roll(t, 1, axis=1)
			tr = np.roll(t, -1, axis=1)
			bl = np.roll(b, 1, axis=1)
			br = np.roll(b, -1, axis=1)
#
			px_sums = np.zeros((Screen.screen_vane_count, Screen.screen_vane_length), dtype=np.byte)
			px_sums += b
			px_sums += t
			px_sums += l
			px_sums += r
			px_sums += tl
			px_sums += tr
			px_sums += bl
			px_sums += br
			gol_arr[px_sums == 3] = True
			gol_arr[px_sums < 3] = False
			gol_arr[px_sums > 4] = False
			gol_arr[px_sums == 4] = np.invert(gol_arr[px_sums == 4])

			time.sleep(0.25)