from skyscreen_core.interface import Screen

import plumbum.cli as cli
from patterns.cli import PatternPlayer, PatternPlayerMixin

#Whatever name you define below make sure to add to __init__.py
class Sample():
        #Blurb about your pattern here

    def __init__(self):
        self.name = "sample"
#Your pattern will be passed a writer, you do not care about this
    def main(self, writer):
        """
        Sample pattern generator
        :param writer: A writer to use
        :type writer: :class:`skyscreen_core.memmap_interface.NPMMAPScreenWriter`
        """
        with writer as writer_buf:
            #This turns the screen into a vane * length * RGB array
            writer_buf_reshaped = writer_buf.reshape((Screen.screen_vane_count, Screen.screen_max_magnitude, 3))

            #Init any pattern stuff you need to here


            #This is the infinite loop your pattern lives inside
            while True:

                #Do some shit with your code to make pretty
                writer_buf_reshaped[:, :, 0] = 254


                #At the end call frame_ready so the writer can take it
                writer.frame_ready()

pattern_class = Sample
