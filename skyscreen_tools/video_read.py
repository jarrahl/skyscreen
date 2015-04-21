"""
Blit a video onto the skyscreen.
"""
import cv2
import sys
import numpy as np
import skyscreen_core.memmap_interface as mm
import skyscreen_core.interface as intf


cap = cv2.VideoCapture(sys.argv[1])
writer = mm.NPMMAPScreenWriter("rendering/foo")
lock = intf.FlockWriterSync("rendering/foo")
# Let's think about this logically.
# We have a 144*4 by 144*4 box. We want to map
# a region of that into polar coordinates. Step one:
# make our 576x576 transform box:
rows = np.resize(np.linspace(-144, 144-1, 576), (576, 576)).T
cols = np.resize(np.linspace(-144, 144-1, 576), (576, 576))
# Then, we apply a transform to it to make it polar:
mag, angle = cv2.cartToPolar(cols, rows)
mag = np.clip(mag, 0, intf.Screen.screen_vane_length-1)
angle = np.clip(angle, 0, intf.Screen.screen_vane_count-1)

with writer as writer_buf:
	buf = writer_buf.reshape((intf.Screen.screen_vane_count, intf.Screen.screen_vane_length, 3))
	while 1:
		ret, frame = cap.read()
		if not ret:
			break
		# So much allocation :(
		subsample = cv2.resize(frame, (160, 90))

		buf[180:270, 0:160, 0] = subsample[:, :, 2] # r -> b
		buf[180:270, 0:160, 1] = subsample[:, :, 1] # g -> g
		buf[180:270, 0:160, 2] = subsample[:, :, 0] # b -> r

		# for row in range(0, 90):
		# 	for col in range(0, 160):
		# 		magn = mag[row, col]
		# 		angl = angle[row, col]
		# 		if np.random.random() < 0.001:
		# 			print magn, angl, row, col
		# 		buf[magn, angl, :] = subsample[row, col, :]


		lock.frame_ready()
		print "FRAME"
print "Video finished, exiting"
cap.release()


