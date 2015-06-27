import logging
import sys
from plumbum import cli
from patterns.cli import PatternPlayerMixin, PatternPlayer

try:
	import theano
	import theano.tensor as T
except ImportError:
	logging.error('You do not have theano! theano. calls will FAIL')
import time
TARGET_FPS = 25

from skyscreen_core.interface import Screen


def theano_scan(writer, draw_fn):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		vane_matrix = [[[vane, vane, vane] for px in range(Screen.screen_max_magnitude)]
					   for vane in range(Screen.screen_vane_count)]
		px_matrix =   [[[px,px*2,px*3] for px in range(Screen.screen_max_magnitude)]
					   for vane in range(Screen.screen_vane_count)]
		vane_vec = T.as_tensor(vane_matrix)
		px_vec = T.as_tensor(px_matrix)
		step = T.fscalar('step')

		draw_fn_with_step = draw_fn(step)
		f, _ = theano.map(draw_fn_with_step, [vane_vec, px_vec])

		fn_actual = theano.function([step], f, allow_input_downcast=True, on_unused_input='ignore')

		step_actual = 0
		while True:
			writer.frame_ready()
			start = time.time()
			writer_buf_reshaped[:] = fn_actual(step_actual)
			step_actual -= 1
			done = time.time()
			fps = 1.0/(done - start)
			if fps < TARGET_FPS:
				logging.warning('Frame rate is %f, which is lower than target %d', fps, TARGET_FPS)
			time.sleep(0.01)

def theano_scan_color(writer, draw_fn):
	with writer as writer_buf:
		writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))
		vane_matrix = [[[float(vane), float(vane), float(vane)] for px in range(Screen.screen_max_magnitude)]
					   for vane in range(Screen.screen_vane_count)]
		px_matrix =   [[[float(px),float(px),float(px)] for px in range(Screen.screen_max_magnitude)]
					   for vane in range(Screen.screen_vane_count)]
		col_matrix =  [[[float(0), float(1), float(2)] for px in range(Screen.screen_max_magnitude)]
					   for vane in range(Screen.screen_vane_count)]
		vane_vec = T.as_tensor(vane_matrix)
		px_vec = T.as_tensor(px_matrix)
		col_vec = T.as_tensor(col_matrix)
		step = T.fscalar('step')

		draw_fn_with_step = draw_fn(step)
		f, _ = theano.map(draw_fn_with_step, [vane_vec, px_vec, col_vec])

		fn_actual = theano.function([step], f, allow_input_downcast=True, on_unused_input='ignore')

		step_actual = 0
		while True:
			writer.frame_ready()
			start = time.time()
			writer_buf_reshaped[:] = fn_actual(step_actual)
			step_actual -= 1
			done = time.time()
			fps = 1.0/(done - start)
			if fps < TARGET_FPS:
				logging.warning('Frame rate is %f, which is lower than target %d', fps, TARGET_FPS)

def theano_swirl(writer):
	def theano_fn(step):
		def draw(vane, px):
			return 127*T.sin((vane+px/2+step)/40.0) + 127*T.sin((vane+px/2+step*1.3)/40.0)
		return draw
	theano_scan(writer, theano_fn)

def theano_tripdar(writer):
	def theano_fn(step):
		def draw(vane, px):
			vane_expr = vane / float(Screen.screen_vane_count) * 3.141
			px_expr = px / float(Screen.screen_max_magnitude)
			step_expr = step
			return 255*T.sin(vane_expr + step_expr/50)*T.sin(px_expr + step_expr/50)
		return draw
	theano_scan(writer, theano_fn)

def theano_radar(writer):
	def theano_fn(step):
		def draw(vane, px, col):
			radar_vane = (step % Screen.screen_vane_count)
			vane_distance = T.clip(((vane - radar_vane) % Screen.screen_vane_count)/Screen.screen_vane_count, 0.0, 1.0)
			vane_expr = T.clip(vane_distance/2.0 + 0.5, 0, 1) * 255

			return T.clip(vane_expr, 0, 255)
		return draw
	theano_scan_color(writer, theano_fn)

def theano_droplet(writer):
	def theano_fn(step):
		def draw(vane, px, col):
			ring = Screen.screen_max_magnitude-(step % Screen.screen_max_magnitude)
			ring_dist = T.maximum(0, float(Screen.screen_max_magnitude)/(ring-px))
			return T.clip(ring_dist, 0, 255)
		return draw
	theano_scan_color(writer, theano_fn)

@PatternPlayer.subcommand("theano-swirl")
class TheanoSwirlCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(theano_swirl)
@PatternPlayer.subcommand("theano-tripdar")
class TheanoTripdarCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(theano_tripdar)
@PatternPlayer.subcommand("theano-radar")
class TheanoRadarCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(theano_radar)
@PatternPlayer.subcommand("theano-droplet")
class TheanoDropletCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(theano_droplet)
