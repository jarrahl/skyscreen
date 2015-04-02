import logging
import os
import tempfile
import argparse

from skyscreen import mmap_interface, rendering, interface


if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('fork_command')
	args = parser.parse_args()

	file_name = tempfile.mktemp("")
	writer = mmap_interface.MMAPScreenWriter(file_name)
	writer.initialize_file()

	reader = mmap_interface.MMAPScreenReader(file_name)
	reader_sync = interface.DummyReaderSync()

	pid = os.fork()
	if pid:
		# The parent does the rendering
		with reader as r:
			rendering.render_main(r, reader_sync, 5)
		os.kill(pid, 9)
	else:
		os.environ['WRITER_FILE'] = file_name
		logging.warning('CWD: %s', os.getcwd())
		prog_split = args.fork_command.split(' ')
		prog = prog_split[0]
		args = prog_split[1:]
		if args:
			os.execl(prog, *args)
		else:
			os.execl(prog, '')
