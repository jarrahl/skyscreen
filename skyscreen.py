import os
import subprocess
import signal
import tempfile
import importlib
import pkgutil

from plumbum import cli

import patterns
import patterns.sample
import skyscreen_core.memmap_interface
import skyscreen_core.interface
import skyscreen_core.udp_interface
import skyscreen_core.bluetooth_receiver
import skyscreen_core.renderer as renderer

class Skyscreen(cli.Application):



    target_filename = cli.SwitchAttr(
        "--video",
        str,
        help="optional. If provided, record output to this file")
    flat_target_filename = cli.SwitchAttr(
        "--flat-video",
        str,
        help="optional. If provided, record raw output to this file")

    fake_run = cli.Flag(
        "--fake-run",
        help="If present, run without displaying, and without forking to background. Useful for profiling"
    )

    no_renderer = cli.Flag(
        "--no-renderer",
        help="Do not run the renderer. This differs from --fake-run in that it still does ZMQ sync and mmap files"
    )

    udp_client = cli.Flag(
        "--udp-client",
        help="Send frames with UDP packets."
    )


    udp_host = cli.SwitchAttr(
        "--udp-port",
        help="The host for the UDP client, including port",
        default="localhost:5555"
    )


    mmap_file = None
    @cli.switch(
        "--mmap-file",
        argtype=str,
        excludes=["--fake-run"],
        mandatory=False,
        help='Overrides the memory mapped file to use'
    )
    def set_mmap_file(self, mmap_file):
        self.mmap_file = mmap_file


    zmq_port = 5555
    @cli.switch(
        "--zmq-port",
        argtype=int,
        excludes=["--fake-run"],
        mandatory=False,
        help='Overrides the zmq port (normally 5555)')
    def set_zmq_port(self, zmq_port):
        self.zmq_port = zmq_port

    def run_displayimage(self, shared_path, python_proc):
        new_env = dict(os.environ.items())
        new_env['WRITER_FILE'] = shared_path
        new_env['LOCK_METHOD'] = 'zmq'
        call = ['python', 'pyrendering/render.py', shared_path]
        if self.target_filename is not None:
            call.append('--output-video')
            call.append(self.target_filename)
        if self.flat_target_filename is not None:
            call.append('--output-raw-video')
            call.append(self.flat_target_filename)
        display = subprocess.Popen(call, env=new_env)
        display.wait()
        os.kill(python_proc, signal.SIGTERM)
        os.waitpid(python_proc, 0)




    def main(self, pattern_name):
        renderer = skyscreen_core.renderer.Renderer(self)
        input = skyscreen_core.bluetooth_receiver.SerialInput("COM4")
        with input as i:
            print i.read_params()
        
        print "Running pattern %s" % pattern_name
        pattern_module = getattr(patterns, pattern_name)
        pattern_class = getattr(pattern_module, 'pattern_class')
        pattern_instance = pattern_class()
        renderer.main_from_renderer(pattern_instance)


if __name__ == '__main__':
    Skyscreen.run()



