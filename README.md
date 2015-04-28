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

# Mac Installation (Also non puppet install) #

Linux users replace brew commands with apt-get and xcode with build-essentials

First make sure you have brew and xcode installed

brew: `ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

xcode: `https://developer.apple.com/xcode/downloads/`

Then run the following
```git clone https://bitbucket.org/ririau/skyscreen.git
brew tap homebrew/science
brew install python opencv cmake zmq 

pip install nose theano numpy scales plumbum cython

python setup.py develop
```

## Building the rendering ##

You shouldn't need to do this - it's done as part of setup.pp, but if you 
need to, here's how:

    cd rendering
    cmake .
    make 

Once you've got cmake to run once, you can just keep using make to build it.

# Running & Testing #

You can test this pretty easily - just run:
 
    nosetests
    
And they should all pass, although they'll spam the screen with some pygame windows.


There are a few ways to run it. The easiest is simply:

    python -m patterns noise
    
This will fork a DisplayImage process, and when you exit the image, it'll exit the python code as well.

If you're getting complicated, you may want to start DisplayImage manually, by calling:

    cd rendering;
    WRITER_FILE=rendering/foo ./DisplayImage
    
and then starting your pattern generator somewhere else. 

