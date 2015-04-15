What are the skyscreen tools?

They're a collection of useful functions and ideas that I hope help you to 
make your own cool visualizations.

Amongst them are:

 - Kaleidoscope tools, to divide the screen up into equal parts and mirror between them
 - Various "propagators" which let your writes to one area propagate to others
 - Tools for composing different screens, to create awesome overlays, in both space and time
 - Video tools, that let you read a video into an area of the screen
 - The fourier transform that you want. Audio goes in, magnitude comes out. No complex number squaring bullshit

These are all implemented with theano, for that speedy speed.

Core Abstractions
=================
We create a set of core abstractions that work in terms of:

 - Mapping matrices, which we use to move things around
   - A Kaleidoscope is then just a set of simple mappings
 - Propagators, which are a little like cellular automata. We define a 
   simple specification language, that is executed in cython. It is executed 
   in a sweep over the bit field. 
 - Memory. In order to perform transforms through time, you must insert data
   into memory, but with limited control over how you insert it - basically, 
   you need to push the whole frame in one go.
 - All the propagators and mappings support application to memory. By
   default they'll only run on the 'surface', in two dimensions, but you're
   quite able to run transforms that will reach back into time through the
   memory to include past values.


The actual problem
------------------
These transforms are all well and good, but they don't really make things _that_
much easier. What I need are easy ways to combine them, ideally visually. Anyway,
that's tomorrow's problem. Today's problem is writing the mapping matrix
implementation.

Bug Log
=======

- Thu Apr  9 22:50:22 AEST 2015 - 86c3da9f2e7bb5f5144dcca214e9972932764509: skyscreen_tools/mapping.py:77
  This was meant to be transposed. It's a pretty obvious issue - the new size is cols by rows, not rows
  by cols. 
- Thu Apr  9 23:15:19 AEST 2015 - 86c3da9f2e7bb5f5144dcca214e9972932764509: skyscreen_tools/mapping.py:55
  I derped and repeated (num_row, num_row), rather than (num_row, num_col). I fixed it while perusing my 
  code.