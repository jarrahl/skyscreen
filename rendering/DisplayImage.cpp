#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <opencv2/opencv.hpp>
#include <sys/file.h>
#include <zmq.h>
#include <stdlib.h>     /* getenv */

using namespace cv;
const char* WINDOW_NAME = "Display Image";
const int WINDOW_SIZE=800;
const int vane_count=360;
const int pixel_count=144*2;
const int array_size=pixel_count*vane_count*3;
const int annulus=50;

int max(int i, int j) {
	if (i > j) return i;
	else return j;
}

#define FILE_LOCK 0
#define ZMQ_LOCK 1

void lock_frame(int lock_method, int fd, void* zmq_resp) {
	if (lock_method == FILE_LOCK)
		flock(fd, LOCK_EX);
	if (lock_method == ZMQ_LOCK) {
		printf("awaiting data\n");
		char buffer[10];
		zmq_recv (zmq_resp, buffer, 10, 0);
		printf("receieved data\n");
	}
}

void unlock_frame(int lock_method, int fd, void* zmq_resp) {
	if (lock_method == FILE_LOCK)
		flock(fd, LOCK_UN);
	if (lock_method == ZMQ_LOCK) {
		 zmq_send (zmq_resp, "UNLOCK", 6, 0);
	}
}

int main(int argc, char** argv )
{
	VideoWriter* writer = NULL;
	if (argc == 2) {
		writer = new VideoWriter(argv[1], CV_FOURCC('P','I','M','1'), 25, Size(WINDOW_SIZE, WINDOW_SIZE), 1);
		printf("WRITING VIDEO to %s\n", argv[1]);
		assert(writer->isOpened());
	}
	Mat A(WINDOW_SIZE, WINDOW_SIZE, CV_8UC3);
	char* filePath = getenv ("WRITER_FILE");
	if (filePath == NULL) {
		printf("You must specify a file in the WRITER_FILE environment variable\n");
		exit(1);
	}
	const int fd = open(filePath, O_RDONLY);
	if (fd == -1) {
		printf("Open file %s failed\n", filePath);
		exit(1);
	}
	char* lock_method_name = getenv ("LOCK_METHOD");
	int lock_method = 0;
	void *zmq_context;
    void *zmq_resp;
	if (lock_method_name == NULL || strcmp(lock_method_name, "file") == 0) {
		lock_method = FILE_LOCK;
	} else {
		printf("USING ZMQ LOCKING\n");
		zmq_context = zmq_ctx_new();
		zmq_resp = zmq_socket (zmq_context, ZMQ_REP);
		int rc = zmq_bind (zmq_resp, "tcp://*:5555");
		assert (rc == 0);
		lock_method = ZMQ_LOCK;
	}


	const unsigned char* data_array = (unsigned char *)mmap(NULL,
		array_size*sizeof(unsigned char), 
		PROT_READ,
		MAP_SHARED,
		(int)fd,
		0);

	printf("Opened successfully\n");
	
	Mat angle(vane_count, pixel_count, CV_32F);
	Mat magnitude(vane_count, pixel_count, CV_32F);
	for (int vane = 0; vane < vane_count; vane++) {
		for (int pixel = 0; pixel < pixel_count; pixel++) {
			float a = vane / ((float)vane_count) * 2.0 * 3.14159;
			float paintable_area = 0.95 * ((WINDOW_SIZE) / 2.0 - annulus);
			float m = annulus + (pixel_count - pixel) / ((float)pixel_count) * paintable_area;
			angle.at<float>(vane, pixel) = a;
			magnitude.at<float>(vane, pixel) = m;
			
		}
	}
	Mat x_coords(vane_count, pixel_count, CV_32F);
	Mat y_coords(vane_count, pixel_count, CV_32F);
	polarToCart(magnitude, angle, x_coords, y_coords);
	float maxmag = 0.0;
	float minmag = 0.0;
	float minx = 0.0;
	float maxx = 0.0;
	float miny = 0.0;
	float maxy = 0.0;

	for (int vane = 0; vane < vane_count; vane++) {
		for (int pixel = 0; pixel < pixel_count; pixel++) {
			if (maxmag < magnitude.at<float>(vane, pixel)) maxmag = magnitude.at<float>(vane, pixel);
			if (minmag > magnitude.at<float>(vane, pixel)) minmag = magnitude.at<float>(vane, pixel);
			if (minx > x_coords.at<float>(vane, pixel)) minx = x_coords.at<float>(vane, pixel);
			if (maxx < x_coords.at<float>(vane, pixel)) maxx = x_coords.at<float>(vane, pixel);
			if (miny > y_coords.at<float>(vane, pixel)) miny = y_coords.at<float>(vane, pixel);
			if (maxy < y_coords.at<float>(vane, pixel)) maxy = y_coords.at<float>(vane, pixel);
		}
	}
	printf("%f\n", maxmag);
	printf("%f\n", minmag);
	printf("%f\n", maxx);
	printf("%f\n", minx);
	printf("%f\n", maxy);
	printf("%f\n", miny);

	namedWindow(WINDOW_NAME, WINDOW_AUTOSIZE);
	char k = -1;
	while(k != (int)'q') {
		imshow(WINDOW_NAME, A);
		if (writer) writer->write(A);
		k = waitKey(1);
		lock_frame(lock_method, fd, zmq_resp);
		for (int vane = 0; vane < vane_count; vane++) {
			for (int pixel = 0; pixel < pixel_count; pixel++) {
				int x = (WINDOW_SIZE/2) + (int)x_coords.at<float>(vane, pixel);
				int y = (WINDOW_SIZE/2) + (int)y_coords.at<float>(vane, pixel);
				assert(x >= 0); assert(x < 800);
				assert(y >= 0); assert(y < 800);
				
				int pixel_pos = vane * (pixel_count * 3) + pixel*3;
				assert(pixel_pos < array_size);
				//printf("%d - %d\n", pixel_pos, array_size);
				unsigned char r = data_array[pixel_pos + 0];
				unsigned char g = data_array[pixel_pos + 1];
				unsigned char b = data_array[pixel_pos + 2];
				//unsigned char r = 255;
				//unsigned char b = 255;
				//unsigned char g = 255;
				A.at<char>(x, y*3+0) = b;
				A.at<char>(x, y*3+1) = g;
				A.at<char>(x, y*3+2) = r;
				A.at<char>(x+1, y*3+0) = b;
				A.at<char>(x+1, y*3+1) = g;
				A.at<char>(x+1, y*3+2) = r;
				A.at<char>(x-1, y*3+0) = b;
				A.at<char>(x-1, y*3+1) = g;
				A.at<char>(x-1, y*3+2) = r;
				A.at<char>(x, y*3+0+3) = b;
				A.at<char>(x, y*3+1+3) = g;
				A.at<char>(x, y*3+2+3) = r;
				A.at<char>(x, y*3+0-3) = b;
				A.at<char>(x, y*3+1-3) = g;
				A.at<char>(x, y*3+2-3) = r;
			}
		}
		unlock_frame(lock_method, fd, zmq_resp);
	}
	return 0;
}

