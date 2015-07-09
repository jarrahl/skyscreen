//
// Created by riri on 5/07/15.
//

#ifndef SKYSCREEN_RECEIVER_RECEIVER_H
#define SKYSCREEN_RECEIVER_RECEIVER_H

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
} ServerS;

typedef ServerS* Server;

Server new_server(bool overwrite_frame);
void free_server(Server s);
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
void receive_frame(Server s);


#endif //SKYSCREEN_RECEIVER_RECEIVER_H
