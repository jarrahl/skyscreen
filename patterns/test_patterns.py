"""
This is to test out flatspace tools.
"""
from patterns.fsm import game_of_life_channel, random_spawn
from patterns import fsm
from skyscreen_core.interface import Screen
import skyscreen_tools.flatspace
import numpy as np
from skyscreen_tools.reshape_wrapper import ReshapingWriterWrapper


def grid(writer):
	reshaped = ReshapingWriterWrapper(writer)
	with reshaped as writer_buf:
		for i in range(0, Screen.screen_vane_count, 20):
			writer_buf[i, :, 0] = 255
		for i in range(0, Screen.screen_max_magnitude, 20):
			writer_buf[:, i, 1] = 255
		while True:
			reshaped.frame_ready()

def simple_lines(writer):
	#with writer as writer_buf:
	#	writer_buf_reshape = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
	#	while True:
	#		writer_buf_reshape[0, :, 0] = 255/4
	#		writer_buf_reshape[90, :, 0] = 255/4*2
	#		writer_buf_reshape[180, :, 0] = 255/4*3
	#		writer_buf_reshape[270, :, 0] = 255
	#		writer_buf_reshape[:, 100, 1] = 255
	#		lock.frame_ready()

	flatspace = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with flatspace as flatspace_buf:
		step = 0
		space = np.resize(np.linspace(0, 254, Screen.screen_vane_count),
						  (Screen.screen_vane_count, Screen.screen_vane_count))
		while False:
			flatspace_buf[:, :, 2] = space
			flatspace_buf[:, :, 1] = space.T
			flatspace_buf[:, :, 0] = 255*np.eye(Screen.screen_vane_count)
			flatspace.frame_ready()
		while True:
			r = step % flatspace_buf.shape[0]
			rn = min((step+50) % flatspace_buf.shape[0], flatspace_buf.shape[0])
			c = step % flatspace_buf.shape[1]
			cn = min((step+50) % flatspace_buf.shape[1], flatspace_buf.shape[1])

			flatspace_buf[r, :, 0] = 0
			flatspace_buf[:, c, 1] = 0
			flatspace_buf[r:rn, c:cn, 2] = 0
			step += 0.5
			r = step % flatspace_buf.shape[0]
			rn = min((step+50) % flatspace_buf.shape[0], flatspace_buf.shape[0])
			c = step % flatspace_buf.shape[1]
			cn = min((step+50) % flatspace_buf.shape[1], flatspace_buf.shape[1])

			flatspace_buf[r, :, 0] = 255
			flatspace_buf[:, c, 1] = 255
			flatspace_buf[r:rn, c:cn, 2] = 255

			flatspace.frame_ready()
