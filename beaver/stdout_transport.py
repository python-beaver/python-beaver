import datetime
import os
import socket
import beaver.transport


class StdoutTransport(beaver.transport.Transport):

    def __init__(self):
        self.current_host = socket.gethostname()

    def callback(self, filename, lines):
        timestamp = datetime.datetime.now().isoformat()
        for line in lines:
            msg = line.strip(os.linesep)
            print "[{0}] [{1}] {2}".format(self.current_host, timestamp, msg)
