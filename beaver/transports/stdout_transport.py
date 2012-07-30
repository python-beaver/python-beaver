import os
import socket

from transport import Transport


class StdoutTransport(Transport):

    def __init__(self):
        self.current_host = socket.gethostname()

    def callback(self, filename, lines):
        for line in lines:
            msg = line.rstrip(os.linesep)
            print "[{0}] {1}".format(self.current_host, msg)
