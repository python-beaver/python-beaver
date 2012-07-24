import os
import simplejson as json
import socket
import zmq

from transport import *

ZEROMQ_ADDRESS = os.environ.get("ZEROMQ_ADDRESS", "tcp://localhost:2120")
ZEROMQ_BIND = os.environ.get("BIND", False)
CURRENT_HOST = socket.gethostname()

CTX = zmq.Context()
PUB = CTX.socket(zmq.PUSH)

if ZEROMQ_BIND:
    PUB.bind(ZEROMQ_ADDRESS)
else:
    PUB.connect(ZEROMQ_ADDRESS)


class AmqpTransport(Transport):

    def callback(self, filename, lines):
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://%s%s" % (CURRENT_HOST, filename),
                '@source_host': CURRENT_HOST,
                '@message': line.rstrip(os.linesep),
                '@source_path': filename
            })
            PUB.send(json_msg)

    def interrupt(self):
        PUB.close()
        CTX.term()

    def unhandled(self):
        return True
