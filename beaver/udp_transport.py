import datetime
import os
import socket

import beaver.transport


class UdpTransport(beaver.transport.Transport):

    def __init__(self, configfile, args):
        super(UdpTransport, self).__init__(configfile, args)

        self.sock = socket.socket(socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP
        self.udp_host = os.environ.get("UDP_HOST", "127.0.0.1")
        self.udp_port = int(os.environ.get("UDP_PORT", 9999))

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for line in lines:
            formatted = self.format(filename, timestamp, line)
            self.sock.sendto(formatted, (self.udp_host, self.udp_port))
