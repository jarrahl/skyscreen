.. the tutorial, where we write a simple pattern

Skyscreen tutorial
==================

In this tutorial, we write a simple pattern. In it, I'll cover:

- The basics of writers and the skyscreen interface
- The basics of the locking system
- How to set up a pattern to work with the other patterns
- How to write your pattern!
- How to use the skyscreen tools to make coding easer

But first, let's imagine a pattern. We'd like to make "bouncybox",
which bounces a rectangle around, like those old DVD players.

Writers and the screen buffer
-----------------------------
The "core abstraction" of all of skyscreen is the skyscreen buffer. Instead of you
having to worry about vanes, and rotation, and tranmitting data, and all that stuff,
all you have to worry about is drawing into the skyscreen buffer. Much simpler!

The buffer is simply a 288*360*3 length buffer of unsigned 8 bit integers. They form
a square, as you'd expect, and contain RGB values. The layout is like this:
::

		        0                   screen_max_magnitude
		        ┌─────────────────────────────────────┐   0
		inside  │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│ outside
		of      │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│  of
		screen                 ...                      screen
		                       ...
		        │rgbrgbrgbrgbrgbrgbgrbgrbgrgbrgbrgbrgb│
		        └─────────────────────────────────────┘ screen_vane_count

And all this can be found in skyscreen_core/interface.py.

There's also a defined way of interacting with the buffers (at least in the python code).
It's defined in :py:class:`skyscreen_core.interface.ScreenWriter`. The key takeaway is
that it uses the with syntax to help deal with setup and cleanup. That's why, throughout
skyscreen code, you see:
::

	with writer as writer_buf:
		...

Python calls the `__enter__` method, which should return the actual buffer into which you
can write, and python calls that the `writer_buf` variable. The cleanup is automatically handled.

Locking
-------
Now, if you just wrote into the skyscreen buffer, there's a good chance that we'd display the
contents of the buffer while it was still being written. Bad news. To avoid that, you need to
signal that you're done with your drawing by calling the writer's `frame_ready()` method. So,
our example becomes a little larger:
::
	with writer as writer_buf:
		while True:
			...
			writer.frame_ready()

Notice that I called `frame_ready()` on `writer`, not on `writer_buf`. Easy mistake to make.

There are several locking implementations, and often you'll need to pass a lock to the writer
when you create the writer. This is handled in the next section.

Implementations
---------------
There several core implementations to choose from:

- :py:class:`skyscreen_core.mmap_interface.MMAPScreenWriter`
- :py:class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
- :py:class:`skyscreen_core.udp_interface.UDPScreenStreamWriter`

Of these, you probably never want to use :py:class:`skyscreen_core.mmap_interface.MMAPScreenWriter`. It
is a reference implementation, far too slow for normal use.

:py:class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter` is a good bet, it's the fast numpy based
implementation that shares data through a mapped file.

:py:class:`skyscreen_core.udp_interface.UDPScreenStreamWriter` is a fancy networked implementation, which
can send screens to remote clients

There are also two locking implementations:

- :py:class:`skyscreen_core.interface.SemaphoreWriterSync` this is for testing purposes
- :py:class:`skyscreen_core.interface.DummyWriterSync` this does nothing - which turns out to be very useful.
- :py:class:`skyscreen_core.interface.FlockWriterSync` this locks though the memory mapped file, but is quite slow
- :py:class:`skyscreen_core.interface.ZMQWriterSync` uses ZMQ (a messaging library) to do the locking. It's fast,
  and it's the one you probably want.


.. warning::
  To be honest, you don't need to worry about these if you're doing patterns. It's handled for you most of the time

Setting up your first pattern file
==================================
Ok, now we're at the good bit! Setting up your first pattern! But first, I need to explain how all the patterns play
nice together.

I use a library called plumbum to stitch together all the patterns and to make them handle command line arguments
nicely. It also means you get a lot of stuff for free! So, what we'll do is to create our pattern file, in
`patterns/dvdbox.py`, and copy paste this into it:
::

	from plumbum import cli
	from patterns.cli import PatternPlayer, PatternPlayerMixin


	@PatternPlayer.subcommand("dvdbox")
	class DVDBox(cli.Application, PatternPlayerMixin):
		def main(self):
			self.main_from_renderer(self.dvdbox)

		def dvdbox(self, writer):
			with writer as writer_buf:
				while True:
					writer.frame_ready()

You then need to change patterns/__init__.py and import dvdbox.

.. note::
If you don't import this, it won't appear in the list of programs available to run


Let's go through all this line by line.

`@PatternPlayer.subcommand` creates a plumbum subcommand. Subcommands are things like the clone in "git clone",
so we're creating a subcommand we'll call with `python quick_render.py dvdbox`.

Next, you see we extend `cli.Application`, which is another plumbum thing. Then we mixin PatternPlayerMixin. This
brings in a whole heap of options and tricks:

- Setting the writer implementation
- Setting the locking implementation
- Setting up video recoding of the output
- Other things - check the mixin!

Then you see the main() function. In here we call `main_from_renderer(self.dvdbox)`. `main_from_renderer` is
provided by PatternPlayerMixin, and it does a bunch of things:

- Sets up the writer
- Sets up the lock
- starts an output reader with appropriate lock implementation as well

Then it calls the function passed to it (`self.dvdbox`, in this case), and passes in the writer, an instance
of :py:class:`skyscreen_core.interface.ScreenWriter`.

So now, let's try it out!
::

	python quick_run.py dvdbox

And you should get ... nothing.

.. note::
	If this complains about Unknown command 'dvdbox', you need to add dvdbox as an import in `patterns/__init__.py`

Drawing a box
-------------
So now let's draw a 20x20 box. This isn't so hard, we just need to write a carefully structured loop, where
we iterate over a few rows, and a few columns, and all the channels, and set them to a value. For fun, we'll
make it pulse with time, so go ahead and edit dvdbox to be:
::

	def dvdbox(self, writer):
		t = 0
		with writer as writer_buf:
			while True:
				writer.frame_ready()
				if t > 255:
					t = 0
				for row in range(0, 20):
					for col in range(0, 20):
						for chan in "rgb":
							writer_buf[pixel_vane_mapping(row, col, chan)] = t
				t += 1
			writer.frame_ready()

This is kind of nasty. It's very manual, and also extremely slow. But hey! We drew a box

.. warning::
	python's loops are shockingly slow, and array access is as well. Avoid doing loops and array access at all costs.
	If you must do these things, use cython, I'm happy to help out, and I know some of the tips and tricks.

Tools and remappings
--------------------

At this point I'm sure you're yearning for something easier to use. In the `skyscreen_tools` directory, there
are a bunch of things to help you out, in particular, there are tools for "flattening" and "reshaping" the
buffer.

- :py:class:`skyscreen_tools.reshape_wrapper.ReshapingWriterWrapper` reshapes the screen to by a 360x288x3 array
- :py:class:`skyscreen_tools.pygame_surface.PygameWritingWrapper` returns a pygame surface rather than an array,
  which is much easier to draw on
- :py:class:`skyscreen_tools.flatspace.FlatSpaceTransform` returns a flattened numpy array, which is in cartesian coordinates,
  not polar.

So, let's try using the reshaping wrapper to make the expression above both simpler and faster:
::

	from plumbum import cli
	from patterns.cli import PatternPlayer, PatternPlayerMixin
	from skyscreen_core.interface import pixel_vane_mapping
	from skyscreen_tools.reshape_wrapper import ReshapingWriterWrapper

	...
	def dvdbox(self, raw_writer):
		t = 0
		writer = ReshapingWriterWrapper(raw_writer)
		with writer as writer_buf:
			while True:
				writer.frame_ready()
				if t > 255:
					t = 0
				writer_buf[0:20, 0:20, :] = t
				t += 1
			writer.frame_ready()

Much simpler, and quite a bit faster! Also note where we've switched our writers to get the numpy version.

Now let's try making the box move instead:
::

	from plumbum import cli
	from skyscreen_tools.flatspace_tools import Screen
	from patterns.cli import PatternPlayer, PatternPlayerMixin
	from skyscreen_core.interface import pixel_vane_mapping
	from skyscreen_tools.reshape_wrapper import ReshapingWriterWrapper

	...
	def dvdbox(self, raw_writer):
		t = 0
		writer = ReshapingWriterWrapper(raw_writer)
		with writer as writer_buf:
			while True:
				writer.frame_ready()
				if t+20 > min(Screen.screen_cols, Screen.screen_rows):
					t = 0
				writer_buf[:] = 0
				writer_buf[t:t+20, t:t+20, :] = 255
				t += 1
			writer.frame_ready()

Notice where we we're checking for the overflow, by referring to `Screen.screen_cols`,  `Screen.screen_rows`.
Nice and abstract. No hard variables.

What's next
===========

You know know all the basics of making patterns! Go make some!