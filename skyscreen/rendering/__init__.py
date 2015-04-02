import pygame
import math
from skyscreen.interface import Screen, pixel_vane_mapping

BLACK = (0, 0, 0)
window_size = 800
annulus_offset = 50
shrinkage_factor = 0.9


def calculate_theta(vane):
	return 2 * math.pi * float(vane) / Screen.screen_vane_count


def calculate_radius(pixel):
	pixel_proportion = float(pixel) / Screen.screen_vane_length
	render_area_size = (window_size / 2 * shrinkage_factor) - annulus_offset
	return annulus_offset + render_area_size * pixel_proportion


def polar_coordinate_transform(theta, radius):
	center = window_size / 2.0
	x = center + radius * math.cos(theta)
	y = center + radius * math.sin(theta)
	return x, y

def render_buffer(screen, reader_buf):
	for vane in xrange(Screen.screen_vane_count):
		theta = calculate_theta(vane)
		for pixel in xrange(Screen.screen_vane_length):
			radius = calculate_radius(pixel)
			x, y = polar_coordinate_transform(theta, radius)
			r = ord(reader_buf[pixel_vane_mapping(vane, pixel, 'r')])
			g = ord(reader_buf[pixel_vane_mapping(vane, pixel, 'g')])
			b = ord(reader_buf[pixel_vane_mapping(vane, pixel, 'b')])
			pygame.draw.ellipse(screen, (r, g, b), [x, y, 10, 10], 5)


def render_main(reader_buf, reader_sync, max_loops=None):
	pygame.init()

	size = (window_size, window_size)
	screen = pygame.display.set_mode(size)

	done = False
	clock = pygame.time.Clock()
	loops = 0
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
		screen.fill(BLACK)
		reader_sync.start_read()

		render_buffer(screen, reader_buf)

		reader_sync.finish_read()
		pygame.display.flip()
		loops += 1
		if max_loops and loops > max_loops:
			done = True

		clock.tick(25)

	pygame.quit()