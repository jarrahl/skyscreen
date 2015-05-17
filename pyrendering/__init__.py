"""
This is a small module that handles rendering to the screen.

Summary
-------

This takes a shared file from the command line. That shared file is expected
to by a memmapped file, which conforms to the :class:`skyscreen_core.interface.ScreenReader`
interface.

It also uses the ZMQ synchronization interface (:class:`skyscreen_core.interface.ZMQReaderSync`).

It reads each frame as it comes in and renders it into two windows. There's the raw window, which
has the raw data in the memmapped file. The other window shows that raw file as the skyscreen would
render it.

Usage
-----
.. warning :: You probably don't want to use this directly. The :mod:`patterns` tools will call it automatically


"""