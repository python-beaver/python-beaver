import os
import simplejson as json
import socket
import zmq

from transport import *


class AmqpTransport(Transport):

    def __init__(self):
        zeromq_address = os.environ.get("ZEROMQ_ADDRESS", "tcp://localhost:2120")
        zeromq_bind = os.environ.get("BIND", False)
        self.current_host = socket.gethostname()

        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUSH)

        if zeromq_bind:
            self.pub.bind(zeromq_address)
        else:
            self.pub.connect(zeromq_address)

    def callback(self, filename, lines):
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://%s%s" % (self.current_host, filename),
                '@source_host': self.current_host,
                '@message': line.rstrip(os.linesep),
                '@source_path': filename
            })
            self.pub.send(json_msg)

    def interrupt(self):
        self.pub.close()
        self.ctx.term()

    def unhandled(self):
        return True
