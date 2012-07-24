import os
import socket

from transport import *

CURRENT_HOST = socket.gethostname()


class StdoutTransport(Transport):

    def callback(self, filename, lines):
        for line in lines:
            msg = line.rstrip(os.linesep)
            print msg
