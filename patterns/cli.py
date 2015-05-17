"""
Using the command line tools

This are convenience tools, that you can use to set up your programs.

The aims are:
 - to allow you to re-use all the run_display stuff, which is quite complex
 - to encourage good CLI tools
 - to let us all inherit a set of command line flags, for videos and whatnot

How to use it
=============

Here's what you *probably* want to do. Write your pattern as a function that
accepts a writer, and has type signature::

	def my_pattern(writer):
		pass #  your code


Now, just above that, add code like this::

	import plumbum.cli as cli
	from patterns.cli import PatternPlayer, PatternPlayerMixin

	@PatternPlayer.subcommand("my_pattern_command")
	class MyPatternCLI(cli.Application, PatternPlayerMixin):
	   def main(self):
		   self.main_from_renderer(my_pattern)

The last thing to do is to make sure your module is imported in `__init__.py`.

.. warning::
    Did you read that last line? Here is is again: The last thing to do is to make sure your module is imported in `__init__.py`.

Now, here are the things to note:
 - ``cli.Application`` as a base class. This is a part of an excellent library called plubmbum,
   and it turns this class into a command line tool.
 - ``@PatternPlayer.subcommand("my_pattern")`` this adds this as a "subcommand" of the PatternPlayer,
   which is itself a CLI appl	ication. You call your sub-command by calling ``python -m patterns 'my_pattern_command``
 - ``self.main_from_renderer(my_pattern)`` passes your pattern function to the rendering tool, which you can find
   in PatternPlayerMixin.

Goodies and Addons
==================
Command line options
--------------------
You can add your own command line options, see https://plumbum.readthedocs.org/en/latest/cli.html
for details

Advanced calls
--------------
What if your renderer has options, that you pass on the command line? Simple: wrap it in a
lambda. See this example, which has an extra awesomeness argument, set as an option::

	@PatternPlayer.subcommand("my_pattern_command")
	class MyPatternCLI(cli.Application, PatternPlayerMixin):
		awesomeness = 10.0
		@cli.switch(['-a', '--awesomeness'], float, help='awesomeness slider')
		def set_awesomeness(self, awesomeness):
			self.awesomeness = awesomeness

		def main(self):
			callback = lambda writer: my_complex_patter(writer, self.awesomeness)
			self.main_from_renderer(callback)

	def my_complex_patter(writer, awesomeness):
		pass  # your code

Troubleshooting
---------------

"""

import os
import subprocess
import signal
import tempfile

import plumbum.cli as cli

import skyscreen_core.memmap_interface
import skyscreen_core.interface


class PatternPlayerMixin(object):
	"""
	This is a mix-in class that you can use to handle almost all the boilerplate
	of writing a command line client.
	"""
	def __init__(self, *args, **kwargs):
		assert isinstance(self, cli.Application), \
			'To use this mixin, your object MUST extend cli.Application'
		super(self, PatternPlayerMixin).__init__(*args, **kwargs)

	target_filename = cli.SwitchAttr(
		"--video",
		str,
		help="optional. If provided, record output to this file")
	flat_target_filename = cli.SwitchAttr(
		"--flat-video",
		str,
		help="optional. If provided, record raw output to this file")

	def run_displayimage(self, shared_path, python_proc):
		new_env = dict(os.environ.items())
		new_env['WRITER_FILE'] = shared_path
		new_env['LOCK_METHOD'] = 'zmq'
		call = ['python', 'pyrendering/render.py', shared_path]
		if self.target_filename is not None:
			call.append('--output-video')
			call.append(self.target_filename)
		if self.flat_target_filename is not None:
			call.append('--output-raw-video')
			call.append(self.flat_target_filename)
		display = subprocess.Popen(call, env=new_env)
		display.wait()
		os.kill(python_proc, signal.SIGKILL)
		os.waitpid(python_proc, 0)

	def main_from_renderer(self, renderer):
		shared_file = tempfile.NamedTemporaryFile()
		pid = os.fork()
		if pid != 0:
			self.run_displayimage(shared_file.name, pid)
			return

		lock = skyscreen_core.interface.ZMQWriterSync()
		writer = skyscreen_core.memmap_interface.NPMMAPScreenWriter(shared_file.name, lock)
		renderer(writer)


class PatternPlayer(cli.Application):
	def main(self, *args):
		if args:
			print "Unknown command %r" % (args[0],)
			return 1  # error exit code
		if not self.nested_command:  # will be ``None`` if no sub-command follows
			print "No command given"
			return 1  # error exit code
