import logging
import os
import tempfile
import argparse
import subprocess
import sys
import traceback

from skyscreen import mmap_interface, rendering, interface


if __name__=='__main__':
	#parser = argparse.ArgumentParser()
	#parser.add_argument('fork_command')
	#args = parser.parse_args()

	#file_name = tempfile.mktemp("")
	file_name = 'foo'
	writer = mmap_interface.MMAPScreenWriter(file_name)
	writer.initialize_file()

	reader = mmap_interface.MMAPScreenReader(file_name)
	reader_sync = interface.DummyReaderSync()


	#pid = os.fork()
	pid = True

	if pid:
		# The parent does the rendering
		logging.warning('Child PID: %d', pid)
		with reader as r:
			rendering.render_main(r, reader_sync)
		os.kill(pid, 9)
	else:
		os.environ['WRITER_FILE'] = file_name
		os.execl('bash', '-c', args.fork_command)
		subprocess.check_call(('/bin/bash', '-c', args.fork_command))
		sys.exit(0)
