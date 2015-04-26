import os
import logging
import random
import tempfile
import time

import skyscreen_core.mmap_interface


filename = tempfile.mktemp("")
sync = skyscreen_core.interface.DummyWriterLock()
writer = skyscreen_core.mmap_interface.MMAPScreenWriter(filename, sync)
writer.initialize_file()
logging.warning('Forking a writer, keeping the reader:')
pid = os.fork()
if pid:
	logging.warning('Forked process is %d', pid)
	with skyscreen_core.mmap_interface.MMAPScreenReader(filename, sync) as reader:
		time.sleep(0.01)  # Settle time
		all_chars_null = True
		for char in reader:
			if char != '\0':
				all_chars_null = False
		os.waitpid(pid, 1)  # Wait for child
		assert not all_chars_null
else:
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename, sync) as writer:
		for i in range(100000):
			offset = random.randint(0, len(writer) - 1)
			c = str(unichr(random.randint(0, 127)))
			writer[offset] = c
