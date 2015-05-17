"""
This module contains various definitions and core functions.

Together, they more or less define the skyscreen interface.

.. note::
Here, we use 'renderer' and 'pattern code' a lot. The renderer is the program that writes to the skyscreen itself.
Pattern code generates the patterns, but doesn't render to the skyscreen.

Overview
========
The skyscreen is has many parts. In order to keep the software simple,
we've created an easy interface for you to use. The contents of the sky screen
are written into a memory-mapped file. The skyscreen can then read from this
file and render it to the screen. This has a bunch of advantages.

- The program that sends the bits to the LEDs will be low level C or C++ code. Using this interface means we can write
  patterns in high level python! Much easier!
- In fact, there's no reason you couldn't write your patterns in whatever language you wanted. It would just need
  to support memory mapping and zmq.
- We also can isolate a lot of the rendering. For example, we can write a cross-fader for patterns by running two
  patterns separately, reading from their mmapped file outputs, and combining that into a new mmapped file output for
  the screne itself
- We make the actual rendering code more crashproof. If things break in the pattern, the skyscreen is unaffected.

Frame Synchronization
---------------------
To signal a frame is ready, we use a simple zmq messenger service. The pattern code sends a message to the renderer
which says 'yo, I'm done, you render now'. The pattern code then renders this frame, and sends a  message back saying
'thanks homie, go do your thing again'. This way we never get tearing or other artifacts from frame sync.


"""