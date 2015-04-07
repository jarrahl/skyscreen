import random
import tempfile
import subprocess

import skyscreen_core.mmap_interface
import skyscreen_core.memmap_interface


def test_writer_open():
	filename = tempfile.mktemp("")
	with skyscreen_core.memmap_interface.NPMMAPScreenWriter(filename) as writer:
		writer[0] = 6

def test_blank_init_to_correct_interface():
	filename = tempfile.mktemp("")
	with skyscreen_core.memmap_interface.NPMMAPScreenWriter(filename) as writer, \
			skyscreen_core.mmap_interface.MMAPScreenReader(filename) as reader:
		for i in range(len(reader)):
			assert ord(reader[i]) == 0, "%d was %s" % (i, reader[i])


def test_send_data_to_correct_interface():
	filename = tempfile.mktemp("")
	with skyscreen_core.memmap_interface.NPMMAPScreenWriter(filename) as writer, \
			skyscreen_core.mmap_interface.MMAPScreenReader(filename) as reader:
		assert len(reader) == len(writer)
		for i in range(100000):
			offset = random.randint(0, len(writer) - 1)
			v = random.randint(0, 255)
			c = chr(v)
			writer[offset] = v
			assert reader[offset] == c

def test_receive_blank_from_correct_interface():
	filename = tempfile.mktemp("")
	with skyscreen_core.mmap_interface.MMAPScreenWriter(filename) as writer, \
			skyscreen_core.memmap_interface.NPMMAPScreenReader(filename) as reader:
		for i in range(len(reader)):
			assert reader[i] == 0, "%d was %s" % (i, reader[i])

def test_receive_datafrom_correct_interface():
	filename = tempfile.mktemp("")
	with skyscreen_core.memmap_interface.NPMMAPScreenWriter(filename) as writer, \
			skyscreen_core.mmap_interface.MMAPScreenReader(filename) as reader:
		assert len(reader) == len(writer)
		for i in range(100000):
			offset = random.randint(0, len(writer) - 1)
			v = random.randint(0, 255)
			c = chr(v)
			writer[offset] = v
			assert reader[offset] == c


def _test_forked_write():
	assert False, 'this is a broken because it forks nose and then we run' \
				  'lots of tests twice.'
	subprocess.check_call("python tests/forked_write.py", shell=True)