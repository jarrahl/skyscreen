from nose import tools
import numpy as np
from skyscreen_core import udp_interface


def test_encode_decode():
	state_vec = 500
	start = 0
	end = 5
	vec = np.zeros(1024).astype(np.uint8)
	packet = udp_interface.encode_packet(state_vec, start, end, vec)
	decoded_state_vec, decoded_start, decoded_end, decoded_vec = udp_interface.decode_packet(packet)
	tools.assert_equals(state_vec, decoded_state_vec)
	tools.assert_equals(start, decoded_start)
	tools.assert_equals(end, decoded_end)
	tools.assert_true(np.all(vec == decoded_vec))
