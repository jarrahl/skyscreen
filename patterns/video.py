import skyscreen_tools.flatspace
import skyscreen_tools.video_read
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("video")
class VideoCLI(cli.Application, PatternPlayerMixin):
	"""
	Render a video to the skyscreen
	"""
	def main(self, video_path):
		callback = lambda writer: video(writer, video_path)
		self.main_from_renderer(callback)

def video(writer, video_path):
	"""
	Render a video to the skyscreen, it will be flattened out

	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	:param video_path: the path of the video we want to render.
	"""
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with reshaped as writer_buf:
		video_blitter = skyscreen_tools.video_read.VideoBliter(writer_buf, video_path, True)
		video_blitter.open()
		while True:
			video_blitter.blit()
			reshaped.frame_ready()