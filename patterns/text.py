import sys
import math
import numpy as np
from skyscreen_core.interface import Screen
import skyscreen_tools.flatspace
import cv2

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

@PatternPlayer.subcommand("text")
class TextCLI(cli.Application, PatternPlayerMixin):
	"""
	An experiment with drawing text to the SkyScreen.
	"""

	def main(self):
		self.main_from_renderer(text)

def writeText(screen, text, pos):
	for x in xrange(5): # For extra thickness/dimensionality
		cv2.putText(screen, text, (pos[0]+x, pos[1]+x), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0))

def createPoint(rows, cols):
	return (int(np.random.random()*rows), int(np.random.random()*cols))

def text(writer):
	"""
	:param writer: A writer to use
	:type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
	"""
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	with reshaped as writer_buf:
		(rows, cols) = writer_buf.shape[:2]
		count = 0
		numpoints = 20
		points = [createPoint(rows, cols) for x in xrange(numpoints)]
		dirs = [np.random.random() * math.pi * 2 for x in xrange(numpoints)]
		speeds = [(np.random.random() * 9 + 2) for x in xrange(numpoints)]
		while True:
			count += 1
			screen = np.zeros((rows, cols, 3))

			# draw a background of gray
			screen[:,:,:] = 20

			writeText(screen, 'asparagus', (110, 230))
			writeText(screen, 'forest', (180, 450))

			# bouncing points
			for i in xrange(len(points)):
				points[i] = (points[i][0] + math.sin(dirs[i])*speeds[i], points[i][1] + math.cos(dirs[i])*speeds[i])
				if points[i][0] < 0 or points[i][0] >= rows:
					# flip on the horizontal axis
					dirs[i] = 2*math.pi - dirs[i]
					points[i] = (min(points[i][0], rows-1), points[i][1])
				if points[i][1] < 0 or points[i][1] >= cols:
					# flip on the vertical axis
					dirs[i] = math.pi - dirs[i]
					if dirs[i] < 0:
						dirs[i] += 2*math.pi
					points[i] = (points[i][0], min(points[i][1], cols-1))

			for i in xrange(len(points)):
				cv2.line(screen, (int(points[i][0]), int(points[i][1])), (int(points[i-1][0]), int(points[i-1][1])), [int((math.sin((count*x)/50.0)+1)*127.5) for x in [1,1.2,1.5]], 2)
			#	cv2.line(screen, ((rows-1)*(i%2),(cols-1)*(i%4 < 2)), (int(points[i][0]), int(points[i][1])), (0, 0, 255), 4)

			#	screen[int(points[i][0]),:,:] = 255;
			#	screen[int(points[i][0]),:,:] = 255;
			#	screen[:,int(points[i][1]),:] = 255;
			writer_buf[:,:,:] = screen
			reshaped.frame_ready()
			sys.stdout.flush()
