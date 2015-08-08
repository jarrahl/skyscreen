import math
import colorsys
import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin
from skyscreen_core.interface import Screen, pixel_vane_mapping
import numpy as np
import cv2
import skyscreen_tools
import pygame
"""
 Wireframe 3D cube simulation.
 Plagiarised from Leonel Machava <leonelmachava@gmail.com>
 http://codeNtronix.com
"""

EPS = 0.00001
class Point3D:
	def __init__(self, x = 0, y = 0, z = 0):
		self.x, self.y, self.z = float(x), float(y), float(z)
	
	def rotateX(self, angle):
		""" Rotates the point around the X axis by the given angle in degrees. """
		rad = angle * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		y = self.y * cosa - self.z * sina + EPS
		z = self.y * sina + self.z * cosa + EPS
		return Point3D(self.x, y, z)
 
	def rotateY(self, angle):
		""" Rotates the point around the Y axis by the given angle in degrees. """
		rad = angle * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		z = self.z * cosa - self.x * sina
		x = self.z * sina + self.x * cosa
		return Point3D(x, self.y, z)
 
	def rotateZ(self, angle):
		""" Rotates the point around the Z axis by the given angle in degrees. """
		rad = angle * math.pi / 180
		cosa = math.cos(rad)
		sina = math.sin(rad)
		x = self.x * cosa - self.y * sina
		y = self.x * sina + self.y * cosa
		return Point3D(x, y, self.z)
 
	def project(self, win_width, win_height, fov, viewer_distance):
		""" Transforms this 3D point to 2D using a perspective projection. """
		factor = fov / (viewer_distance + self.z)
		x = self.x * factor + win_width / 2
		y = -self.y * factor + win_height / 2
		return Point3D(x, y, 1)

@PatternPlayer.subcommand("cube")
class CubeCLI(cli.Application, PatternPlayerMixin):
	def main(self):
		self.main_from_renderer(cube_render)

def cube_render(writer):
	reshaped = skyscreen_tools.flatspace.FlatSpaceTransform(writer)
	surfWriter = skyscreen_tools.pygame_surface.PygameWritingWrapper(reshaped)
	t = 0
	vertices = [
		Point3D(-1,1,-1),
		Point3D(1,1,-1),
		Point3D(1,-1,-1),
		Point3D(-1,-1,-1),
		Point3D(-1,1,1),
		Point3D(1,1,1),
		Point3D(1,-1,1),
		Point3D(-1,-1,1)
	]
	faces = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]

	angleX, angleY, angleZ = 0, 0, 0
	count = 0
	with surfWriter as writer_buf:
		while True:
			writer_buf.fill((0, 0, 0))
			t = []
			
			for v in vertices:
				# Rotate the point around X axis, then around Y axis, and finally around Z axis.
				r = v.rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
				# Transform the point from 3D to 2D
				r = r.project(writer_buf.get_width(), writer_buf.get_height(), 256, 2.5)
				# Put the point in the list of transformed vertices
				t.append(r)

			for f in faces:
				points = [(t[i].x, t[i].y) for i in f]
				pygame.draw.lines(writer_buf, np.array(colorsys.hsv_to_rgb(math.sin(count/100.0)/2 + 0.5, 1, 1))*255, True, points, 3)
				
			angleX = angleY = angleZ = count

			surfWriter.frame_ready()
			count += 1

