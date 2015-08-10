import logging
import numpy as np
import shlex
import tempfile
import plumbum.cli as cli
import os
import subprocess
import sys
import signal
from patterns.cli import PatternPlayer, PatternPlayerMixin
import skyscreen_core.interface
import skyscreen_core.memmap_interface
import atexit

# TODO: Fix this
left_port = int(np.random.random()*1000) + 5000
right_port = int(np.random.random()*1000) + 5000

combine_funcs = {
"behind": lambda x, y: np.fmax(x * 0.3, y),
"avg": lambda x, y: (x+y)/2,
"and": lambda x, y: x & y,
"or": lambda x, y: x | y,
"xor": lambda x, y: x ^ y,
"max": lambda x, y: np.fmax(x, y),
"sum": lambda x, y: (x + y) % 256,
"diff": lambda x, y: (x - y + 256) % 256,
}

@PatternPlayer.subcommand("combine")
class CombineCLI(cli.Application, PatternPlayerMixin):
	def main(self, program_left, operator, program_right):
		"""
		Spawn out two subprograms for left and right, then make a
		renderer from the two of them. They can be combined by
		'avg', 'and', 'or', 'xor' or 'max'.
		:param program_left:
		:param operator:
		:param program_right:
		:return:
		"""
		logging.warning("In case of unusual termination, this can "
						"leave backgroun python processes around! If you experience issues"
						"or if it terminates abnormally, run 'prgrep python' to look for"
						"backgroun processes.")
		self.left_file = tempfile.NamedTemporaryFile().name
		self.right_file = tempfile.NamedTemporaryFile().name

		if operator not in combine_funcs:
			print "Operator '" + operator + "' is not valid. Valid operators are", ", ".join(combine_funcs.keys())
			sys.exit(1)

		self.combine_func = combine_funcs[operator]

		# Here we're using these to initialize the screens data files
		# that's why they're so weird and why they don't have a lock implementation
		left_writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(self.left_file, None)
		right_writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(self.right_file, None)
		with left_writer as _, right_writer as _:
			pass  # Initialize the data files, then close it all down.

		call_args = ["python", "quick_run.py"]
		pid_left = os.fork()
		if pid_left == 0:
			left_args = shlex.split(program_left)
			left_additional_args = ['--no-renderer', '--mmap-file', self.left_file, '--zmq-port', str(left_port)]
			os.execvp("python", call_args + left_args + left_additional_args)
			# We should NEVER get here, it means the underlying pattern died
			assert False, "The left pattern has exited, so we're exploding"
		else:
			atexit.register(kill_subtask_callback(pid_left))

		pid_right = os.fork()
		if pid_right == 0:
			right_args = shlex.split(program_right)
			right_additional_args = ['--no-renderer', '--mmap-file', self.right_file, '--zmq-port', str(right_port)]
			os.execvp("python", call_args + right_args + right_additional_args)
			# We should NEVER get here, it means the underlying pattern died
			assert False, "The right pattern has exited, so we're exploding"
		else:
			atexit.register(kill_subtask_callback(pid_right))


		self.main_from_renderer(self.combine)

	def combine(self, writer):
		# These lock and reader implementations are in here so we can
		# avoid forking, which causes them to crash over contention for the socket.
		left_lock = skyscreen_core.interface.ZMQReaderSync(left_port)
		right_lock = skyscreen_core.interface.ZMQReaderSync(right_port)

		self.left_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(self.left_file, left_lock)
		self.right_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(self.right_file, right_lock)


		with writer as writer_buf, \
			self.left_reader as left_buf, \
			self.right_reader as right_buf:
			while True:
				logging.debug('Entering left read')
				self.left_reader.start_read()
				logging.debug('Entering right read')
				self.right_reader.start_read()
				logging.debug('Copying')
				writer_buf[:] = self.combine_func(left_buf, right_buf)
				logging.debug('Finishing right read')
				self.right_reader.finish_read()
				logging.debug('Finishing left read')
				self.left_reader.finish_read()
				logging.debug('Frame ready')
				writer.frame_ready()
				logging.debug('Finished')


def kill_subtask_callback(pid):
	def kill():
		logging.warning("Sending SIGTERM to %d" % pid)
		os.kill(pid, signal.SIGTERM)
		os.waitpid(pid, 0)
		logging.warning("%d has exited" % pid)
	return kill
