import numpy as np
import scipy.ndimage.filters as filters
import time
from skyscreen_core.interface import Screen



def game_of_life_channel(gol_arr):
	right = np.roll(gol_arr, 1)
	left = np.roll(gol_arr, -1)
	down = np.roll(gol_arr, 1, axis=0)
	up = np.roll(gol_arr, -1, axis=0)
	upright = np.roll(left, 1, axis=0)
	upleft = np.roll(left, -1, axis=0)
	downright = np.roll(right, 1, axis=0)
	downleft = np.roll(right, -1, axis=0)

	px_sums = np.zeros(gol_arr.shape, dtype=np.byte)
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

def init_gliders(gol_arr):
	for i in range(0, 100, 5):
		gol_arr[i+0, i+1] = True
		gol_arr[i+1, i+2] = True
		gol_arr[i+2, i+0] = True
		gol_arr[i+2, i+1] = True
		gol_arr[i+2, i+2] = True

		gol_arr[i+1+10, i+0] = True
		gol_arr[i+2+10, i+1] = True
		gol_arr[i+0+10, i+2] = True
		gol_arr[i+1+10, i+2] = True
		gol_arr[i+2+10, i+2] = True


		gol_arr[i-1+144, i+0] = True
		gol_arr[i-2+144, i+1] = True
		gol_arr[i-0+144, i+2] = True
		gol_arr[i-1+144, i+2] = True
		gol_arr[i-2+144, i+2] = True

def init_random(gol_arr):
	gol_arr[:] = np.round(
		abs(np.random.random((Screen.screen_vane_count, Screen.screen_max_magnitude)) - 0.3)
	)

def random_spawn(gol_arr):
	region_size = (10, 10)
	start = (
		np.random.randint(0, Screen.screen_vane_count-region_size[0]),
		np.random.randint(0, Screen.screen_max_magnitude-region_size[1])
	)
	gol_arr[start[0]:start[0]+10, start[1]:start[1]+10] = np.round(
		abs(np.random.random((10, 10)) - 0.3)
	)


def game_of_life(writer, sub_prog='random'):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))


		gol_arr_r = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude), dtype=bool)
		gol_arr_g = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude), dtype=bool)
		gol_arr_b = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude), dtype=bool)
		gol_arr_d = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude), dtype=bool)


		if sub_prog == 'random':
			# init_random(gol_arr_r)
			# init_random(gol_arr_g)
			# init_random(gol_arr_b)
			# init_random(gol_arr_d)
			brightness = 20.0
		elif sub_prog == 'gliders':
			init_gliders(gol_arr_r)
			init_gliders(gol_arr_g)
			init_gliders(gol_arr_b)
			brightness = 10.0

		while True:
			game_of_life_channel(gol_arr_r)
			game_of_life_channel(gol_arr_g)
			game_of_life_channel(gol_arr_b)
			game_of_life_channel(gol_arr_d)
			if np.random.random() < 0.2 and sub_prog == 'random':
				random_spawn(gol_arr_r)
				random_spawn(gol_arr_g)
				random_spawn(gol_arr_b)
				random_spawn(gol_arr_d)
			#writer_buf_reshaped[:, :, 0] = gol_arr_r * 255
			#writer_buf_reshaped[:, :, 1] = gol_arr_g * 255
			#writer_buf_reshaped[:, :, 2] = gol_arr_b * 255
			writer_buf_reshaped[:, :, 0] += brightness * gol_arr_r % 255
			writer_buf_reshaped[:, :, 1] += brightness * gol_arr_g % 255
			writer_buf_reshaped[:, :, 2] += brightness * gol_arr_b % 255
			writer_buf_reshaped[:, :, 0] *= np.invert(gol_arr_d)
			writer_buf_reshaped[:, :, 1] *= np.invert(gol_arr_d)
			writer_buf_reshaped[:, :, 2] *= np.invert(gol_arr_d)
			writer.frame_ready()


import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand('gameoflife')
class MyPatternCLI(cli.Application, PatternPlayerMixin):
	sub_program = cli.SwitchAttr('--subprogram', cli.Set('gliders', 'random'), mandatory=True)
	def main(self):
		call = lambda writer: game_of_life(writer, self.sub_program)
		self.main_from_renderer(call)
