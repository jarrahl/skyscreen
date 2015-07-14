.. Skyscreen documentation master file, created by
   sphinx-quickstart on Sun May 17 14:24:19 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Skyscreen's documentation!
=====================================
Here, you'll find documentation on our awesome skyscreen. Looking for somewhere to start? Check out patterns!

Building these docs
-------------------
* Ensure sphynx is installed, most likely by doing
::

   pip install Sphinx

* Then go
::

   cd docs
   make apidoc && make html

Setup
=====
Linux
-----
You should install using puppet. It makes life simple. Using your package manager, install puppet.
then, run::

   git clone https://bitbucket.org/ririau/skyscreen.git
   cd skyscreen
   cp setup.pp.skeleton setup.pp
   vim setup.pp # At this point you should edit the user and paths at the top of the file
   sudo puppet module install stankevich-python
   sudo puppet apply setup.pp

If there are errors, it is most likely because your package manager and mine have different package
names. That's on you buddy!

OSX
---

First you need brew and xcode to start installing everything else

* brew
::

   ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

* xcode
::

   https://developer.apple.com/xcode/downloads/

Then run the following::

   git clone https://bitbucket.org/ririau/skyscreen.git
   brew tap homebrew/science 
   brew install python opencv cmake zmq git
   brew install mercurial sdl sdl_image sdl_mixer sdl_ttf smpeg portmidi

   pip install nose theano numpy scales plumbum cython msgpack-python
   pip install hg+http://bitbucket.org/pygame/pygame

   python setup.py develop

Running
-------
If your chosen installation method succeeded, you should be good to go!
Just run
::

   python quick_run.py bands

And you'll be rewarded with a pattern (I hope).

For good luck, you can also run the test suite. Simply running nosetests should do it,
::

   nosetests

Starting to program
===================
Where to begin? Check out :doc:`tutorial` which takes you through writing a simple pattern.

If you're interested in the internal workings and how we structure and send data, go take a look
at :doc:`skyscreen_core/modules`. If you're interested in writing something that isn't quite a pattern,
but makes it easier to write patterns, then :doc:`skyscreen_tools/modules` is where you should look,
although if you're trying to do this, you'll definitely need to understand the core modules anyway.


Contents:
=========

.. toctree::
   :maxdepth: 1
   :glob:

   patterns/modules
   pyrendering/modules
   skyscreen_core/modules
   skyscreen_tools/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

