import cv2
import numpy as np
from plumbum import cli
from greplin import scales
import skyscreen_core.interface as interface
import skyscreen_core.memmap_interface
import skyscreen_tools.reshape_wrapper
import pyximport;

pyximport.install()
import pyrendering.fast_tools


def create_windows():
	cv2.namedWindow('raw_image', cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)


def destroy_windows():
	cv2.destroyAllWindows()


class MainRender(cli.Application):
	output_location = None
	window_size = 800
	annulus = 50

	@cli.switch("--output-video", str)
	def set_output_video(self, filename):
		self.output_location = filename

	def make_mapping_matrix(self):
		paintable_area = 0.95 * (self.window_size / 2.0 - self.annulus)
		angles = np.zeros((interface.Screen.screen_vane_count, interface.Screen.screen_vane_length))
		magnitudes = np.zeros((interface.Screen.screen_vane_count, interface.Screen.screen_vane_length))
		for angle in xrange(interface.Screen.screen_vane_count):
			for mag in xrange(interface.Screen.screen_vane_length):
				render_angle = angle / float(interface.Screen.screen_vane_count) * 2.0 * 3.14159
				render_mag = self.annulus + (interface.Screen.screen_vane_length - mag) / \
											float(interface.Screen.screen_vane_length) * paintable_area
				angles[angle, mag] = render_angle
				magnitudes[angle, mag] = render_mag
		cols, rows = cv2.polarToCart(magnitudes, angles)
		cols = np.round((cols + self.window_size / 2)).astype(np.int32)
		rows = np.round((rows + self.window_size / 2)).astype(np.int32)

		return cols, rows

	def main(self, shared_file):
		lock = interface.ZMQReaderSync()
		raw_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(shared_file, lock)
		reader = skyscreen_tools.reshape_wrapper.ReshapingWriterReader(raw_reader)

		polar_image = np.zeros((self.window_size, self.window_size, 3), dtype=np.uint8)
		raw_image = np.zeros((self.window_size, self.window_size, 3), dtype=np.uint8)

		cols, rows = self.make_mapping_matrix()

		create_windows()
		with reader as reader_buf:
			bgr_fixed = np.zeros(reader_buf.shape, dtype=np.uint8)

			while True:
				# Fix up BGR color, turn it to RGB
				# This also means we copy in the image, so we can
				# hand back to the render ASAP.
				reader.start_read()
				bgr_fixed[:, :, 0] = reader_buf[:, :, 2]
				bgr_fixed[:, :, 1] = reader_buf[:, :, 1]
				bgr_fixed[:, :, 2] = reader_buf[:, :, 0]
				reader.finish_read()
				cv2.resize(bgr_fixed, (self.window_size, self.window_size), raw_image)
				pyrendering.fast_tools.quickblit(
					bgr_fixed,
					polar_image,
					rows,
					cols)
				cv2.imshow('raw_image', raw_image)
				cv2.imshow('image', polar_image)
				char = cv2.waitKey(1)
				if char != -1:
					break

		destroy_windows()


if __name__ == '__main__':
	MainRender.run()