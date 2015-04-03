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
 - Performance
 - Performance
 - Performance
 
At the moment there's a _huge_ bottleneck in the shared array. I'm confident that the shared
array can be fast enough to work, meaning that the OS is not the problem here. There are bottle-necks in
the type-conversion from int to byte, which can be solved with a more intelligent cast, or by
working only with c-types. Then there's a large bottleneck on the other side when reading the
array and copying into the surface.

I may try using the blit() method to apply the shared array straight onto the surface, assuming
that it's all in the right order. 

One option I'm hoping will work is that numpy will let me treat the mmapped array as a numpy 
array. Then we'll be all good.

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

