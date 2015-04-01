import random
import string
import tempfile
import threading
import skyscreen.mmap_interface


def test_writer_open():
	filename = tempfile.mktemp("")
	with skyscreen.mmap_interface.MMAPScreenWriter(filename) as writer:
		writer[0] = 'a'


def test_reader_open():
	filename = tempfile.mktemp("")
	with skyscreen.mmap_interface.MMAPScreenWriter(filename) as writer:
		writer[0] = 'a'

	with skyscreen.mmap_interface.MMAPScreenReader(filename) as reader:
		assert reader[0] == 'a'


def test_blank_init():
	filename = tempfile.mktemp("")
	with skyscreen.mmap_interface.MMAPScreenWriter(filename) as writer, \
			skyscreen.mmap_interface.MMAPScreenReader(filename) as reader:
		for i in range(len(reader)):
			assert (reader[i] == '\0')


def test_send_data():
	filename = tempfile.mktemp("")
	with skyscreen.mmap_interface.MMAPScreenWriter(filename) as writer, \
			skyscreen.mmap_interface.MMAPScreenReader(filename) as reader:
		assert len(reader) == len(writer)
		for i in range(100000):
			offset = random.randint(0, len(writer) - 1)
			c = str(unichr(random.randint(0, 127)))
			writer[offset] = c
			assert reader[offset] == c
# FIXME: the trick with testing the sync stuff is to write a class that deals with
# sync. Then mock that class, with a queue that lets me sneak in other clients and stuff.