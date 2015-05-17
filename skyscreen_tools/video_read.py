"""
Blit a video onto the skyscreen.
"""
import cv2


class VideoBliter(object):
	"""
	Blit a video into some memory. This takes a numpy array,
	and a path to the video, and returns a "video blitter".

	- it has an 'open' method that you need to call to
	open the video file
	- it has a 'close' method that will close the video file
	- when you call its 'blit()' method, it'll blit in a frame
	of the video, and advance to the next video.
	- it will resize the video to be the size of the memory_slice
	- if repeat is set to true, the video will loop
	- if repeat is set to false, then blit() will throw an EOFError
	when the video ends.
	"""

	def __init__(
			self,
			memory_slice,
			video_path,
			repeat=False):
		"""
		:param memory_slice: the region to blit into
		:param video_path: the path for the video
		:param repeat: if true, loop the video (default false)
		:return:
		"""
		self.repeat = repeat
		assert len(memory_slice.shape) == 3, \
			"memory_slice must be a 3D array"
		assert memory_slice.shape[2] == 3, \
			"the 3rd dimension must have size 3 (RGB)"
		self.memory_slice = memory_slice
		self.video_path = video_path
		self.cap = None

	def open(self):
		self.cap = cv2.VideoCapture(self.video_path)

	def close(self):
		self.cap.release()

	def blit(self):
		assert self.cap is not None, \
			'You must call open() before running'
		ret, frame = self.cap.read()
		video_size = self.memory_slice.shape[:2]
		if not ret:
			raise EOFError
		subsample = cv2.resize(frame, video_size)
		self.memory_slice[:, :, 0] = subsample[:, :, 2]  # r -> b
		self.memory_slice[:, :, 1] = subsample[:, :, 1]  # g -> g
		self.memory_slice[:, :, 2] = subsample[:, :, 0]  # b -> r
