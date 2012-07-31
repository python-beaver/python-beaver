import os
import socket
from datetime import datetime

from transport import Transport


class StdoutTransport(Transport):

    def __init__(self):
        self.current_host = socket.gethostname()

    def callback(self, filename, lines):
        timestamp = datetime.now().isoformat()
        for line in lines:
            msg = line.rstrip(os.linesep)
            print "[{0}] [{1}] {2}".format(self.current_host, timestamp, msg)
