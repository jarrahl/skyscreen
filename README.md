# Skyscreen #
This is the python code I'm working on for skyscreen. It's meant to be sort of language agnostic. 
At it's heart is a communications method that can be used by pretty much any programming language.

# Real docs #

We have docs! You can read them in the docs dir (perhaps look at index.rst), and you can build them
and read them, and hopefully find answers. They include the installation instructions.

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

