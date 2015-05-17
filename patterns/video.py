import skyscreen_tools.flatspace
import skyscreen_tools.video_read
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("video")
class VideoCLI(cli.Application, PatternPlayerMixin):
	def main(self, video_path):
		callback = lambda writer: video(writer, video_path)
		self.main_from_renderer(callback)

def video(writer, video_path):
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with reshaped as writer_buf:
		video_blitter = skyscreen_tools.video_read.VideoBliter(writer_buf, video_path, True)
		video_blitter.open()
		while True:
			video_blitter.blit()
			reshaped.frame_ready()