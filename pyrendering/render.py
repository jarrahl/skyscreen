import cv2
import numpy as np
from plumbum import cli
import skyscreen_core.interface as interface
import skyscreen_core.memmap_interface
import skyscreen_tools.reshape_wrapper
import fast_tools

from skyscreen_core.interface import Screen

def _create_windows():
	cv2.namedWindow('raw_image', cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)


def _destroy_windows():
	cv2.destroyAllWindows()


class MainRender(cli.Application):
	_output_location = None
	_raw_output_location = None
	_window_size = 800
	_annulus = 50

	@cli.switch("--output-video", str)
	def _set_output_video(self, filename):
		assert filename[-4:] == '.avi', 'video file must end in .avi'
		self._output_location = filename

	@cli.switch("--output-raw-video", str)
	def _set_raw_output_video(self, filename):
		assert filename[-4:] == '.avi', 'video file must end in .avi'
		self._raw_output_location = filename

	def _make_mapping_matrix(self):
		paintable_area = 0.95 * (self._window_size / 2.0 - self._annulus)
		angles = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude))
		magnitudes = np.zeros((Screen.screen_vane_count, Screen.screen_max_magnitude))
		for angle in xrange(Screen.screen_vane_count):
			for mag in xrange(Screen.screen_max_magnitude):
				render_angle = (angle+0.5) / float(Screen.screen_vane_count) * 2.0 * 3.14159
				render_mag = self._annulus + (Screen.screen_max_magnitude - mag) / \
											float(Screen.screen_max_magnitude) * paintable_area
				angles[angle, mag] = render_angle
				magnitudes[angle, mag] = render_mag
		cols, rows = cv2.polarToCart(magnitudes, angles)
		cols = np.round((cols + self._window_size / 2)).astype(np.int32)
		rows = np.round((rows + self._window_size / 2)).astype(np.int32)

		return cols, rows

	def main(self, shared_file):
		"""
		Run the renderer.

		:param shared_file:
			the interface file. It should conform to the :class:`skyscreen_core.interface.ScreenReader` interface
		"""
		lock = interface.ZMQReaderSync()
		raw_reader = skyscreen_core.memmap_interface.NPMMAPScreenReader(shared_file, lock)
		reader = skyscreen_tools.reshape_wrapper.ReshapingWriterReader(raw_reader)

		polar_image = np.zeros((self._window_size, self._window_size, 3), dtype=np.uint8)
		cols, rows = self._make_mapping_matrix()

		_create_windows()
		if self._output_location:
			fourcc = cv2.cv.CV_FOURCC(*'XVID')
			out = cv2.VideoWriter(
				self._output_location,
				fourcc,
				25.0,
				(self._window_size, self._window_size)
			)
			if not out.isOpened():
				raise IOError('Could not open file %s for some reason' % self._output_location)
		else:
			out = None

		if self._raw_output_location:
			fourcc = cv2.cv.CV_FOURCC(*'XVID')
			# There turns out to be a minimum size for xvid, so we scale up 2x
			rawout = cv2.VideoWriter(
				self._raw_output_location,
				fourcc,
				25.0,
				(Screen.screen_vane_count*2, Screen.screen_max_magnitude*2)
			)
			if not rawout.isOpened():
				raise IOError('Could not open file %s for some reason' % self._raw_output_location)
		else:
			rawout = None

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
				raw_image = cv2.resize(bgr_fixed, (Screen.screen_vane_count*2, Screen.screen_max_magnitude*2))
				reader.finish_read()
				fast_tools.quickblit(
					bgr_fixed,
					polar_image,
					rows,
					cols)
				cv2.imshow('raw_image', bgr_fixed)
				cv2.imshow('image', polar_image)
				if out is not None:
					out.write(polar_image)
				if rawout is not None:
					rawout.write(raw_image)

				char = cv2.waitKey(1)
				if char != -1:
					break
		_destroy_windows()
		if out is not None:
			out.release()
		if rawout is not None:
			rawout.release()


if __name__ == '__main__':
	MainRender.run()
