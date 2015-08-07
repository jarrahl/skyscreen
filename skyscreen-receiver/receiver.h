/** ********** USING THE RECEIVER ************** 
 * How does it work?
 * ==================
 *
 * The receiver works by creating a UDP server, and 
 * reading parts of the skyscreen into a buffer. It 
 * keeps three buffers, internally:
 * - The output buffer. This one is public, and you can
 *   read from it safely without it changing
 * - And two internal buffers, one for the screen that is
 *   currently being received, and one for the next screen
 *   long.
 * There are two buffers for ordering issues in UDP where we
 * may see an out of order packet.
 *
 * You create the server with new_server. This takes one
 * argument, explained in the *fast_mode* section. This will
 * return an initalized server.
 *
 * You should call first_frame() after creating the server.
 * This will lock the mutex, so that you can immediately
 * render from it.
 *
 * Then, call (in some other thread) receive_frames(), which
 * starts the server loop. 
 *
 * In your code, you should be rendering screenfuls, then
 * calling switch_frame(), which gives the server a chance
 * to shuffle around the frames. By the time switch_frame()
 * returns, you're guaranteed that:
 *  - The output frame will be updated, if possible
 *  - There will be no more changes to the output frame 
 *    until you call switch_frame() again.
 *
 * Once you're finished with the server:
 * 1. Shut down your code. 
 * 2. Call last_frame()
 * 4. Call terminate_server()
 * 5. Call free_server()
 *
 * In these steps, you release the lock, so that later the 
 * free_server() call can delete it, then you stop the 
 * server with terminate_server(), and finally you free
 * the server memory.
 *
 * But we both know you're just going to send SIGINT instead.
 * That's cool.
 *
 * fast_mode
 * ---------
 *
 * One of the easiest ways to get good performance is to limit
 * copy operations. To that end, you can enable "fast mode". In
 * slow mode, the output_frame always is at the same address,
 * and data for it is copied into it. This can be useful if you
 * don't have a nice way to change the frame address in your 
 * rendering code, or if you find it faster overall to assume a
 * constant address.
 *
 * On the other hand, if you _can_ handle the output_frame's 
 * address changing (at a known time), then you'll get better 
 * performance by setting fast_mode to true. When fast mode is 
 * true, the output_frame may change.
 *
 * In both modes, the ONLY time that there will be a change is
 * during the frame_pause() or first_frame() calls.
 *
 * Startup sequence
 * ----------------
 * 1. Call new_server       - Parent thread, this reference will
 *                            be shared between the two threads
 * 2. Split into threads
 * 3. Call initalize_server - Server thread    | The interleaving
 * 4. Call first_frame      - Renderer thread  | of server & 
 * 5. Call receive_frames   - Server thread    | renderer doens't
 * 6. Call frame_pause over - Renderer thread  | matter.
 *    and over
 *
 *
 * Shutdown sequence
 * -----------------
 * 1. Stop the render loop  - Render thread
 * 2. Call last_frame       - Render thread
 * 3. Call terminate_server - Server thread
 * 4. Call free_server      - Server thread
 * 5. Join the thread
 *
 * (or just SIGINT the whole process)
 */
#ifndef SKYSCREEN_RECEIVER_RECEIVER_H 
#define SKYSCREEN_RECEIVER_RECEIVER_H
#include <pthread.h>

typedef unsigned char* Frame;

unsigned int FRAME_ITEMS = 288*360*3;
unsigned int FRAME_SIZE = 288*360*3 * sizeof(unsigned char);

typedef struct ServerS {
    Frame output_frame;
    Frame current_frame;
    Frame next_frame;
    unsigned char msg[65507];
    unsigned char msg_decomp[65507];
    unsigned char state_vec;
    int sockfd;
    unsigned char n_nextframes;
    unsigned char n_ignored;
    unsigned char max_nextframes;
    unsigned char max_ignores;
    // While frame_lock is held, you're
    // guaranteed that output_frame will 
    // not change. Please use the frame_pause()
    // function to lock/unlock the mutex.
    pthread_mutex_t frame_lock;

    bool fast_mode;
} ServerS;

typedef ServerS* Server;

// In fast mode, the _pointer_ to output_frame
// is updated, while in slow mode, the 
// actual value of output_frame is updated.
// 
// This lets you pick between having a constant 
// frame at all times, or having it potentially change,
// but being faster (there's no memcpy).
Server new_server(bool fast_mode);
// Call frame pause every rendering, it gives
// us a chance to update your frame.
// This will return the output frame for you
Frame frame_pause(Server s);
// This signals that the system is about to start,
// and returns the output frame, like frame_pause()
Frame first_frame(Server s);
void free_server(Server s);
void last_frame(Server s);
void initalize_server(Server s, char* port);
void terminate_server(Server s);
/**
 * Receive a frame from the server. The way that this
 * works is to sit around and wait for enough packets
 * to come in that we see a new frame packet.
 *
 * After calling, the caller may inspect the ServerS'
 * current_frame and read from it safely. Please note
 * that the server WILL change
 */
void receive_frames(Server s);


#endif //SKYSCREEN_RECEIVER_RECEIVER_H
