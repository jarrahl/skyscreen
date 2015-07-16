//
// Created by riri on 5/07/15.
//
#include <assert.h>
#include <errno.h>
#include <iostream>
#include <msgpack.hpp>
#include <netdb.h>
#include <netinet/in.h>
#include "receiver.h"
#include <stdarg.h>
#include <zlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <iosfwd>
#include "string"


unsigned long int max_msg_len = 65507;
void process_message(Server s, char * msg_decomp, unsigned long received_uncompressed);

static void die (int line_number, const char * format, ...) {
    va_list vargs;
    va_start (vargs, format);
    fprintf (stderr, "%d: ", line_number);
    vfprintf (stderr, format, vargs);
    fprintf (stderr, ".\n");
    exit (1);
}

Frame new_frame() {
    Frame f = (unsigned char *)calloc(FRAME_ITEMS, sizeof(unsigned char));
    return f;
}

void free_frame(Frame f) {
    free(f);
}

Server new_server() {
    Server s = (ServerS *)calloc(1, sizeof(ServerS));
    assert(s != NULL);
    s->output_frame = new_frame();
    s->current_frame = new_frame();
    s->next_frame = new_frame();
    s->max_nextframes = 2;
    s->max_ignores = 2;

    return s;
}

void free_server(Server s) {
    free_frame(s->output_frame);
    free_frame(s->current_frame);
    free_frame(s->next_frame);
    free(s);
}

void initalize_server(Server s, const char* port) {
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_DGRAM;
    hints.ai_protocol = 0;
    hints.ai_flags = AI_PASSIVE|AI_ADDRCONFIG;

    struct addrinfo* res = 0;
    int err = getaddrinfo("0", port, &hints, &res);

    if (err != 0) {
        die(__LINE__, "%s, failed to resolve local socket address (err=%d)", __FILE__, err);
    }
    int fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (fd==-1) {
        die(__LINE__, "%s: %s", __FILE__, strerror(errno));
    }
    if (bind(fd, res->ai_addr, res->ai_addrlen) == -1) {
        die(__LINE__, "%s: %s", __FILE__, strerror(errno));
    }
    freeaddrinfo(res);
    s->sockfd = fd;
}

void terminate_server(Server s) {
    close(s->sockfd);
}


typedef std::map<std::string, msgpack::object> MapStrMsgPackObj;

void receive_frame(Server s) {
    assert(s->sockfd);

    while (1) {
        int received = recv(s->sockfd, s->msg, max_msg_len, 0);
        unsigned long received_uncompressed = max_msg_len;
        int err = uncompress(s->msg_decomp, &received_uncompressed, s->msg, received);
        if (err == Z_OK) {
            process_message(s, (char *)(s->msg_decomp), received_uncompressed);
        }
    }
}

void increment_frame(Server s) {
    s->state_vec++;
    memcpy(s->output_frame, s->current_frame, FRAME_SIZE);
    Frame tmp = s->next_frame;
    s->next_frame = s->current_frame;
    s->current_frame = tmp;
    s->n_nextframes = 0;
    s->n_ignored = 0;
}

void update_frame(Frame f, MapStrMsgPackObj mmap) {
    // Early exit if fields aren't found.
    if (!(mmap.count("start") &&
        mmap.count("end") &&
        mmap.count("vec"))) return;
    unsigned int start = mmap["start"].via.u64;
    unsigned int end = mmap["end"].via.u64;
    msgpack::object_raw data = mmap["vec"].via.raw;
    unsigned char* raw_chardata = (unsigned char*)data.ptr;
    for (unsigned int i = 0;
         i + start < end &&
         i < data.size &&
         i < FRAME_SIZE;
         i++) {
        f[i+start] = raw_chardata[i];
    }
}

void process_message(Server s,
                     char * msg_decomp,
                     unsigned long received_uncompressed) {
    std::string str(msg_decomp, received_uncompressed);

    msgpack::unpacked result;
    msgpack::unpack(&result, str.data(), str.size());

    msgpack::object deserialized = result.get();

    // msgpack::object supports ostream.
    MapStrMsgPackObj mmap = deserialized.as<MapStrMsgPackObj>();
    int state_vec = mmap["state_vec"].via.u64;
    bool is_eof = mmap.count("start") == 1;
    /*
     * How to decide where to handle a message.
     * 1) Check if it's state vec is current state + 1
     *    - If so, put into the next frame
     *    - Increment the nextframe counter
     *    - If the nextframe counter is too large, we move to the next frame
     * 2) Check if it's state vec is more than current state + 1
     *    - If so, ignore it
     *    - And increment the ignore counter by one
     *    - If the ignore counter is too large, we reset both the current and
     *      next frames, to zero, and write in the packet to the current frame,
     *      and then set the current frame to the output frame
     * 3) Otherwise, we just write directly into the frame
     * 4) If it's a nextframe signal, and it's state vec matches the current frame,
     *    then we swap
     *    - If it does not match, we ignore it.
     */

    if (state_vec == s->state_vec) {
        if (is_eof) {
            increment_frame(s);
        } else {
            update_frame(s->current_frame, mmap);
        }
    } else {
        if (state_vec == s->state_vec + 1) {
            if (is_eof) {
                increment_frame(s);
            }else{
                update_frame(s->next_frame, mmap);

                s->n_nextframes++;
                if (s->n_nextframes > s->max_nextframes) {
                    increment_frame(s);
                }
            }
        } else {
            s->n_ignored++;
            if (s->n_ignored > s->max_ignores) {
                s->state_vec = state_vec;
                if (is_eof){
                    update_frame(s->current_frame, mmap);
                }
                memcpy(s->output_frame, s->current_frame, FRAME_SIZE);
            }
        }
    }
}


int main() {
    Server s = new_server();
    std::string port = "5555";
    initalize_server(s, port.c_str());

    receive_frame(s);
    terminate_server(s);
    free_server(s);
}