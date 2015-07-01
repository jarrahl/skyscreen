"""
A UDP server and client for skyscreen.

The client/writer is quite simple, it simply sends data willynilly to the
host and port it was given.

The server/reader is extremely complex, and it does a whole lot of threading
and stuff. It's not the best.

The reader
----------
The reader is split between four classes:

1. UDPScreenStreamReader: this is the class you'll call to create your reader.
   It acts just like a normal reader.
2. UDPScreenStreamThread: when you call the UDPScreenStreamReader's __enter__()
   method, it spawns a UDPScreenStreamThread and starts it running. This thread
   will contain the actual UDP server.
3. UDPServerWithArgs: in order to pass some variables into the actual socket
   server, we override SocketServer.UDPServer and add in our own data and lock
   variables, and then the handler can use self.server.data and self.server.lock
   to access them.
4. UDPScreenStream: the actual handler.

**Locking and synchronization**
We use one threading.Lock lock to handle the synchronization. When a read is in
progress (between start_read and finish_read) the lock is held by the reader
thread (as opposed to the server thread, which is UDPScreenStreamThread).

The thread is held by the server most of the time, as it constructs the image
from packets.

The lock is created by UDPScreenStreamReader and passed to UDPScreenStreamThread.
Just before starting the actual server, in the UDPScreenStreamThread's run() method,
the server will acquire the lock - because the first thing it does is to await
image data. Then, once a frame has been assembled, the lock is released,
presumably to a waiting UDPScreenStreamReader, which should have called
start_read(). Immediately after releasing, the UDP server will try to reacquire
the lock, and start building the frame again.

**The exit and cleanup process**
When the UDPStreamReader hits its __exit__() method, it'll call the
UDPScreenStreamThread's close() method. Note that this DOES NOT HAPPEN IN
THE SERVER THREAD. Anyway, it calls close, which calls the UDPServerWithArgs's
server_close() method, which causes the server to shut down. This seems to
close the underlying socket, causing the server thread to shit it's pants and
throw a socket.error exception. We intercept it, and ignore it.

Finally, both threads will try to release the lock. One of them has it, so the
other one will throw and exception, which is also ignored.

The UDPScreenStreamReader will wait for the server thread to join, before leaving
it's __exit__ method.

Transport format
----------------
To maximize speed, the transport format is binary. It two packet types:

1. An "end of frame" packet
2. A "data" packet.

They're encoded using msgpack.

Update algorithm
----------------
"""
import SocketServer
import logging
import socket
import datetime
import threading
import thread
import zlib

import numpy as np

import skyscreen_core.interface
import msgpack


MAX_PACKET_SIZE = 63500
MAX_ITEMS = 50000

pack = lambda msg: msgpack.packb(msg)
unpack = lambda msg: msgpack.unpackb(msg)
# pack = lambda msg: yaml.dump(msg)
# unpack = lambda msg: yaml.load(msg)

def encode_packet(state_vec, start, end, vec):
	packet = {
		'state_vec': state_vec,
		'start': int(start),
		'end': int(end),
		'vec': str(vec.newbyteorder('<').data)
	}
	data_encoded = zlib.compress(pack(packet))
	assert len(data_encoded) < MAX_PACKET_SIZE, \
		'The encoded data was too big for UDP'
	return data_encoded


def encode_end_of_frame(state_vec):
	packet = {
		'state_vec': state_vec
	}
	data_encoded = pack(packet)
	return zlib.compress(data_encoded)


def decode_packet(packet):
	decompressed_packet = zlib.decompress(packet)
	try:
		packet = unpack(decompressed_packet)
	except msgpack.exceptions.UnpackValueError:
		logging.warning('Decode error')
		return None, None, None, None
	state_vec = packet['state_vec']
	if 'start' in packet:
		start = packet['start']
		end = packet['end']
		vec = np.frombuffer(packet['vec'], dtype=np.uint8).newbyteorder('N')
	else:
		start = None
		end = None
		vec = None
	return state_vec, start, end, vec


class UDPScreenStreamWriter(skyscreen_core.interface.ScreenWriter):
	def __init__(self, reader_host, reader_port=5555):
		self.underlying_screen = np.zeros(self.array_size, dtype=np.uint8)
		self.reader_host = reader_host
		self.reader_port = reader_port
		self._addr_info = (reader_host, reader_port)

		self._state_vec = 0
		self._frame_starts = np.arange(0, self.array_size, MAX_ITEMS - 1)
		self.total_sent = 1
		self.total_frames = 1

	def frame_ready(self):
		self._state_vec += 1
		if self._state_vec > 255:
			self._state_vec = 0
		for start in self._frame_starts:
			end = start + MAX_ITEMS - 1
			_send_vec = self.underlying_screen[start:end]
			packet_data = encode_packet(self._state_vec, start, end, _send_vec)
			self.total_sent += self.sock.sendto(packet_data, self._addr_info)

		packet_data = encode_end_of_frame(self._state_vec)
		self.total_sent += self.sock.sendto(packet_data, self._addr_info)
		self.total_frames += 1

	def __enter__(self):
		logging.info('Using UDP client, server: %s, port %d', self.reader_host, self.reader_port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.start_time = datetime.datetime.now()
		return self.underlying_screen

	def __exit__(self, type, value, traceback):
		self.sock.close()
		self.end_time = datetime.datetime.now()
		dt = (self.end_time - self.start_time).total_seconds() + 1

		sent_packets = self.total_sent / (1024.0 ** 2)
		speed = sent_packets / dt

		print ""
		print "SENT: %f M Bytes" % sent_packets
		print "Speed: %f M Bytes/s" % speed
		print 'Data per frame: %f M Bytes' % (sent_packets / self.total_frames)
		print 'Data at 25fps: %f M Bytes/s' % ((sent_packets / self.total_frames) * 25)
		print 'Data at 30fps: %f M Bytes/s' % ((sent_packets / self.total_frames) * 30)


class UDPScreenStreamReader(skyscreen_core.interface.ScreenReader):
	def __init__(self, listen_host, listen_port):
		self.listen_port = listen_port
		self.listen_host = listen_host

	def __enter__(self):
		self.lock = threading.Lock()
		self.data = np.zeros(self.array_size, dtype=np.uint8)
		self.server = UDPScreenStreamThread(
			self.lock,
			self.data,
			self.listen_host,
			self.listen_port)
		self.server.start()
		return self.data

	def __exit__(self, type, value, traceback):
		self.server.close()
		try:
			self.lock.release()
		except thread.error:
			logging.info(
				'Error while releasing lock, we probably '
				'don\'t hold it.\n'
				'Not actually a problem')
			pass
		logging.info('Waiting for the server thread to exit')
		self.server.join()
		logging.info('Server thread has joined, cleanup finished')

	def finish_read(self):
		logging.info('Releasing lock in finish read')
		self.lock.release()

	def start_read(self):
		logging.info('Waiting to acquire lock in start_read')
		self.lock.acquire()
		assert self.server.isAlive(), 'Server died'
		logging.info('Read starts')


class UDPScreenStreamThread(threading.Thread):
	def __init__(self, lock, data, host, port):
		self.data = data
		self.lock = lock
		self.port = port
		self.host = host
		self.server = None
		self.cleanup_in_progress = False
		super(UDPScreenStreamThread, self).__init__()

	def run(self):
		logging.info('Acquiring lock to safely start server')
		self.lock.acquire()
		logging.info('Starting server')
		logging.info('Starting server host "%s" port %d', self.host, self.port)
		try:
			self.server = UDPServerWithArgs(self.lock, self.data, (self.host, self.port), UDPScreenStream)
			self.server.serve_forever()
		except socket.error as e:
			if e.errno == 9 and self.cleanup_in_progress:
				logging.info(
					'Caught error in server, but it looks like'
					'it was in the middle of cleanup.')
			else:
				raise
		finally:
			try:
				self.lock.release()
			except thread.error:
				logging.info(
					'Error while releasing lock (in server), we probably '
					'don\'t hold it.\n'
					'Not actually a problem')
				pass
		logging.info('Server exited, thread quitting')

	def close(self):
		logging.info('Closing server')
		self.cleanup_in_progress = True
		if self.server:
			self.server.server_close()
		logging.info('Server closed')


class UDPServerWithArgs(SocketServer.UDPServer):
	def __init__(self, lock, data, server_address, request_handler_class):
		self.max_packet_size = MAX_PACKET_SIZE
		SocketServer.UDPServer.__init__(self, server_address, request_handler_class)
		self.data = data
		self.lock = lock


class UDPScreenStream(SocketServer.BaseRequestHandler):
	def handle(self):
		packet = self.request[0]
		decoded = decode_packet(packet)

		logging.info('Releasing lock for start_read')
		# We sometimes crash here on exit,
		# when the server is closing anyway.
		self.server.lock.release()
		logging.info('Waiting to reacquire lock')
		self.server.lock.acquire()
		logging.info('Got lock!')