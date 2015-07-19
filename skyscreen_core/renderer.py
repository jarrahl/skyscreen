

import os
import tempfile
import subprocess

import memmap_interface
import interface
import udp_interface

class Renderer(object):

    def __init__(self, skyscreen):
        self.skyscreen = skyscreen

    def run_displayimage(self, shared_path, python_proc):
        new_env = dict(os.environ.items())
        new_env['WRITER_FILE'] = shared_path
        new_env['LOCK_METHOD'] = 'zmq'
        call = ['python', 'pyrendering/render.py', shared_path]
        if self.skyscreen.target_filename is not None:
            call.append('--output-video')
            call.append(self.skyscreen.target_filename)
        if self.skyscreen.flat_target_filename is not None:
            call.append('--output-raw-video')
            call.append(self.skyscreen.flat_target_filename)
        display= subprocess.Popen(call, env=new_env)
        display.wait()
        os.kill(python_proc, signal.SIGTERM)
        os.waitpid(python_proc, 0)

    def main_from_renderer(self, renderer):
        shared_file_name = tempfile.NamedTemporaryFile().name if self.skyscreen.mmap_file is None else self.skyscreen.mmap_file

        run_renderer = not self.skyscreen.no_renderer and not self.skyscreen.fake_run and not self.skyscreen.udp_client
        if run_renderer:
            pid = os.fork()
            if pid != 0:
                self.run_displayimage(shared_file_name, pid)
                return
        if self.skyscreen.fake_run or self.skyscreen.udp_client:
            lock = interface.DummyWriterSync()
        else:
            lock = interface.ZMQWriterSync(self.skyscreen.zmq_port)

        if self.skyscreen.udp_client:
            host_port = self.skyscreen.udp_host.split(':')
            assert len(host_port) <= 2, 'Address must have format hostname:port, or hostname (default port is 5555)'
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) == 2 else 5555
            writer = udp_interface.UDPScreenStreamWriter(host, port)
        else:
            writer = memmap_interface.NPMMAPScreenWriter(shared_file_name, lock)

        renderer.main(writer)


