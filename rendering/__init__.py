import pygame
import pyximport
pyximport.install()
from rendering import renderops
from skyscreen.interface import Screen, pixel_vane_mapping

BLACK = (0, 0, 0)
window_size = 800
annulus_offset = 50
shrinkage_factor = 0.9

def render_buffer(surf, reader_buf):
	for vane in xrange(Screen.screen_vane_count):
		theta = renderops.calculate_theta(vane)
		for pixel in xrange(Screen.screen_vane_length):
			radius = renderops.calculate_radius(pixel)
			x, y = renderops.polar_coordinate_transform(theta, radius)
			r = reader_buf[pixel_vane_mapping(vane, pixel, 'r')]
			g = reader_buf[pixel_vane_mapping(vane, pixel, 'g')]
			b = reader_buf[pixel_vane_mapping(vane, pixel, 'b')]

			surf[x][y] = [r, g, b]
			surf[x + 1][y] = [r, g, b]
			surf[x - 1][y] = [r, g, b]
			surf[x][y + 1] = [r, g, b]
			surf[x][y - 1] = [r, g, b]


def render_main(reader_buf, reader_sync, max_loops=None, callback=None):
	pygame.init()

	size = (window_size, window_size)
	screen = pygame.display.set_mode(size)

	done = False
	clock = pygame.time.Clock()
	loops = 0
	surf = pygame.surfarray.pixels3d(screen)
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
		screen.fill(BLACK)
		reader_sync.start_read()

		# renderops.render_buffer(surf, reader_buf)
		render_buffer(surf, reader_buf)

		reader_sync.finish_read()
		pygame.display.flip()
		loops += 1
		if max_loops and loops > max_loops:
			done = True
		if callback:
			callback()

		clock.tick(25)

	pygame.quit()