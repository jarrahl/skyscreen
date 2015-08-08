/*
These are the fastest blit tools I could write.

YOU PROBABLY SHOULDN'T BE HERE. USE skyscreen_tools.flatspace INSTEAD

There are two functions:
 - blit_polar: map input to output, moving from flatspace into polar coordinates. This asssumes you've previously
   called initalize_globals.
 - initalize_globals: set up a global mapping from mags and angle to row and coumn.

 See flatspace_tools for the actual use in python

Compilation: gcc -shared -o libflatspace_faster.so -fPIC flatspace_faster.c -O3
 */

#include <unistd.h>
#include <stdio.h>

#define screen_max_magnitude 288
#define screen_cols 288
#define screen_vane_count 360
#define screen_rows 360
#define window_size 800
#define annulus 50
#define paintable_area (288*2+50*2)

unsigned char setup = 0;
unsigned int mags[paintable_area][paintable_area];
unsigned int angles[paintable_area][paintable_area];

// Set up the global mappings, by passing in an array of points.
// Each point on the flatspace screen should correspond to a mag
// and angle on the skyscreen screen.
void initialize_globals(
	unsigned int mag_vals[paintable_area][paintable_area],
	unsigned int angle_vals[paintable_area][paintable_area]) {
	unsigned int i, j;
	for (i = 0; i < paintable_area; i++) {
		for (j = 0; j < paintable_area; j++) {
			mags[i][j]   =   mag_vals[i][j];
			angles[i][j] = angle_vals[i][j];
		}
	}
	setup = 1;
}

// A sneaky little inline file
inline void blit_inner(
	unsigned int row,
	unsigned int col,
	unsigned int mag,
	unsigned int angle,
	unsigned char input[paintable_area][paintable_area][3],
	unsigned char output[screen_rows][screen_cols][3]
	) {
	output[angle][mag][0] = input[row][col][0];
	output[angle][mag][1] = input[row][col][1];
	output[angle][mag][2] = input[row][col][2];
}

// Blit from the flatspace input to the polar output.
void blit_polar(unsigned char input[paintable_area][paintable_area][3], unsigned char output[screen_rows][screen_cols][3]) {
	unsigned int row, col;

	if (setup == 0) {
		printf("CALL initialize_globals FIRST\n");
		printf("I will now CRASH!\n");
		_exit(1);
	}

	for (row = 0; row < paintable_area; row++) {
		for (col = 0; col < paintable_area; col++) {
			unsigned int mag =     mags[row][col];
			unsigned int angle = angles[row][col];
			if (
				mag >= 0
				&& angle >= 0
				&& mag < screen_max_magnitude
			    && angle < screen_vane_count) {
				blit_inner(row, col, mag, angle, input, output);
			}
		}
	}
}
