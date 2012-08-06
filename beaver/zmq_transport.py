import datetime
import os
import socket
import ujson as json
import zmq

import beaver.transport


class ZmqTransport(beaver.transport.Transport):

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
        timestamp = datetime.datetime.now().isoformat()
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
            self.pub.send(json_msg)

    def interrupt(self):
        self.pub.close()
        self.ctx.term()

    def unhandled(self):
        return True
