import random
import tempfile
import subprocess

import skyscreen_core.mmap_interface


def test_writer_open():
	filename = tempfile.mktemp("")
	writer_lock = skyscreen_core.interface.DummyWriterSync()
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename, writer_lock) as writer:
		writer[0] = 'a'


def test_reader_open():
	filename = tempfile.mktemp("")
	writer_lock = skyscreen_core.interface.DummyWriterSync()
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename, writer_lock) as writer:
		writer[0] = 'a'
	reader_lock = skyscreen_core.interface.DummyReaderSync()
	with skyscreen_core.mmap_interface.MMAPScreenReader(filename, reader_lock) as reader:
		assert reader[0] == 'a'


def test_blank_init():
	filename = tempfile.mktemp("")
	writer_lock = skyscreen_core.interface.DummyWriterSync()
	reader_lock = skyscreen_core.interface.DummyReaderSync()
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename, writer_lock) as writer, \
			skyscreen_core.mmap_interface.MMAPScreenReader(filename, reader_lock) as reader:
		for i in range(len(reader)):
			assert (reader[i] == '\0')


def test_send_data():
	filename = tempfile.mktemp("")
	writer_lock = skyscreen_core.interface.DummyWriterSync()
	reader_lock = skyscreen_core.interface.DummyReaderSync()
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename, writer_lock) as writer, \
			skyscreen_core.mmap_interface.MMAPScreenReader(filename, reader_lock) as reader:
		assert len(reader) == len(writer)
		for i in range(100000):
			offset = random.randint(0, len(writer) - 1)
			c = str(unichr(random.randint(0, 127)))
			writer[offset] = c
			assert reader[offset] == c


def _test_forked_write():
	assert False
	subprocess.check_call("python tests/forked_write.py", shell=True)