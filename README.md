# Skyscreen #
This is the python code I'm working on for skyscreen. It's meant to be sort of language agnostic. At it's heart is a communications method that can be used by pretty much any programming language.

## Communication ##
The 'skyscreen communication' standard has two parts:
1. An large array of bytes, each byte being a pixel's color's intensity. 
2. A 'flush' method which signals that the frame is ready for display.

For the receiver, it's more or less the same, but the 'flush' method has two parts, one where it acquires the memory area and one where it releases it back to the writer.

## Implementation ##
The current implementation uses a memory mapped file that we can share between writer and reader, and a semaphore to implement flush, but I'll be abstracting out the flush synchronization mechanism for testability (at some point).

In the future I'd like to implement:

1. Mode flags, so we can have the option to buffer some screens or to change interlacing
2. A UDP based synchronization protocol so that we can easily write over network links.
3. A way to compose transforms of the byte-array, which might be a good way to implement interlacing and such.

# TODO #
The next thing to do is to write a display module so we can all start testing our patterns. Then to write a C receiver for speed. Note that if we managed the network sync protocol, we could get away from using linux on the reciever pie, and use a real time OS instead.

# Installation #

- Install pygame
- Install nosetests - sadly, I haven't quite worked out how to get pygame installed in a venv, so you'll have to 
  install it in the global python rep. Sorry. Anyway, do a:
 
     sudo pip install nose
  
- And you're good to go

# Running & Testing #

You can test this pretty easily - just run:
 
    nosetests
    
And they should all pass, although they'll spam the screen with some pygame windows.

To run it, you've got a few option. The number one option is to use the rendering module:

    python -m skyscreen.rendering
    
This will use the file 'foo' in the CWD as the mmap region. Once you've started this process, you can
start your own code to write to that region. To test everything is working as expected, try running 
an example screen:
    
    WRITER_FILE=foo python -m screens noise
    
Once you're finished, just kill the processes.