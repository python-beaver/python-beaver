import datetime
import os
import zmq

import beaver.transport


class ZmqTransport(beaver.transport.Transport):

    def __init__(self, configfile):
        super(ZmqTransport, self).__init__(configfile)

        zeromq_address = os.environ.get("ZEROMQ_ADDRESS", "tcp://localhost:2120")
        zeromq_bind = os.environ.get("BIND", False)

        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUSH)

        if zeromq_bind:
            self.pub.bind(zeromq_address)
        else:
            self.pub.connect(zeromq_address)

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().isoformat()
        for line in lines:
            self.pub.send(self.format(filename, timestamp, line))

    def interrupt(self):
        self.pub.close()
        self.ctx.term()

    def unhandled(self):
        return True
