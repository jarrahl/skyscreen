# Skyscreen #
This is the python code I'm working on for skyscreen. It's meant to be sort of language agnostic. 
At it's heart is a communications method that can be used by pretty much any programming language.

## Communication ##
The 'skyscreen communication' standard has two parts:
1. An large array of bytes, each byte being a pixel's color's intensity. 
2. A 'flush' method which signals that the frame is ready for display.

For the receiver, it's more or less the same, but the 'flush' method has two parts, 
one where it acquires the memory area and one where it releases it back to the writer.

## Implementation ##
The current implementation uses a memory mapped file that we can share between writer and reader, 
and a semaphore to implement flush, but I'll be abstracting out the flush synchronization mechanism 
for testability (at some point).

In the future I'd like to implement:

1. Mode flags, so we can have the option to buffer some screens or to change interlacing
2. A UDP based synchronization protocol so that we can easily write over network links.
3. A way to compose transforms of the byte-array, which might be a good way to implement interlacing and such.

# Installation #

- Clone the repo
- Install puppet
- Copy setup.pp.skeleton to setup.pp, making changes to the variables base_path and user
- sudo puppet apply setup.pp
- **you need to 'activate' your virtual environment. run:```source env/bin/activate``` to do so. You need to do this 
  in each new terminal, so that when you call python it's the one in env**
  (you can check by executing ```which python```, and it should be inside env/bin.
- You should be good to go
- If you have import issues with theano, do ```pip install theano``` (again in the virtual environment). The puppet 
  script can be a bit dodgy sometimes.
- If you use a GPU, then you should run your screens with the GPU theano flags. I successfully used:
 ```
 THEANO_FLAGS=device=gpu,floatX=float32,print_active_device=True
```
Although this hasn't yielded any large speedups that I can see, but I'm not sure if that's just because the computation isn't very complex.



## Building the rendering ##

You shouldn't need to do this - it's done as part of setup.pp, but if you 
need to, here's how:

- cd rednering
- cmake .
- make 

Once you've got cmake to run once, you can just keep using make to build it.

# Running & Testing #

You can test this pretty easily - just run:
 
    nosetests
    
And they should all pass, although they'll spam the screen with some pygame windows.

To run it, you've got a few options. The number one option is to use the rendering system in the rendering directory:

    cd rendering; WRITER_FILE=foo ./DisplayImage

This will use the file 'foo' in the CWD as the mmap region. Once you've started this process, you can
start your own code to write to that region. You'll need to do this in another term though, because the 
display must continue to run:
    
    # also remmeber to activate the new window's python env
    WRITER_FILE=rendering/foo python -m screens noise
    
Once you're finished, just kill the processes.