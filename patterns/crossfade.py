import logging
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

left_port = 5556
right_port = 5557

@PatternPlayer.subcommand("crossfader")
class CrossFaderCLI(cli.Application, PatternPlayerMixin):
	# TODO: args for left & right port, and for how to start the system (eg, --call="python -m patterns")
	def main(self, program_left, program_right):
		"""
		Spawn out two subprograms for left and right, then make a
		renderer from the two of them
		:param program_left:
		:param program_right:
		:return:
		"""
		logging.warning("You have chosen to use the CROSSFADER. Congradulations!")
		logging.warning("However, in case of unusual termination, it can "
						"leave backgroun python processes around! If you experience issues"
						"or if it terminates abnormally, run 'prgrep python' to look for"
						"backgroun processes.")
		self.left_file = tempfile.NamedTemporaryFile().name
		self.right_file = tempfile.NamedTemporaryFile().name

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


		self.main_from_renderer(self.crossfade)

	def crossfade(self, writer):
		# These lock and reader implementations are in here so we can
		# avoid forking, which causes them to crash over contention for the socket.
		left_lock = skyscreen_core.interface.ZMQReaderSync(left_port)
		right_lock = skyscreen_core.interface.ZMQReaderSync(right_port)

		self.left_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(self.left_file, left_lock)
		self.right_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(self.right_file, right_lock)


		with writer as writer_buf, \
			self.left_reader as left_buf, \
			self.right_reader as right_buf:
			t = 0.0
			dt = 0.01
			while True:
				logging.debug('Entering left read')
				self.left_reader.start_read()
				logging.debug('Entering right read')
				self.right_reader.start_read()
				logging.debug('Copying')
				writer_buf[:] = t * left_buf + (1-t) * right_buf
				t += dt
				if t > 1.0 or t < 0.0:
					dt = -dt
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