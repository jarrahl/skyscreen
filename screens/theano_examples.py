import logging
import sys
import time
TARGET_FPS = 25

from skyscreen_core.interface import Screen


def theano_scan(writer, lock, style='swirl'):
	try:
		import theano
		import theano.tensor as T
	except ImportError:
		logging.error("Theano not found, exiting")
		sys.exit(1)
	else:
		logging.warning("You're using theano! Nice! You may want to look into the runtime flags")

	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_vane_length, 3))
		vane_matrix = [[[vane, vane, vane] for px in range(Screen.screen_vane_length)]
					   for vane in range(Screen.screen_vane_count)]
		px_matrix =   [[[px,px*2,px*3] for px in range(Screen.screen_vane_length)]
					   for vane in range(Screen.screen_vane_count)]
		vane_vec = T.as_tensor(vane_matrix)
		px_vec = T.as_tensor(px_matrix)
		step = T.fscalar('step')

		if style=='swirl':
			def draw(vane, px):
				return 127*T.sin((vane+px/2+step)/40.0) + 127*T.sin((vane+px/2+step*1.3)/40.0)
		else:
			def draw(vane, px):
				vane_expr = vane / float(Screen.screen_vane_count) * 3.141
				px_expr = px / float(Screen.screen_vane_length)
				step_expr = step
				return 255*T.sin(vane_expr + step_expr/50)*T.sin(px_expr + step_expr/50)

		f, _ = theano.map(draw, [vane_vec, px_vec])

		fn_actual = theano.function([step], f, allow_input_downcast=True)

		step_actual = 0
		while True:
			lock.frame_ready()
			start = time.time()
			writer_buf_reshaped[:] = fn_actual(step_actual)
			step_actual -= 1
			done = time.time()
			fps = 1.0/(done - start)
			if fps < TARGET_FPS:
				logging.warning('Frame rate is %f, which is lower than target %d', fps, TARGET_FPS)

