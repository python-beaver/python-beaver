import datetime
import socket

import beaver.transport


class UdpTransport(beaver.transport.Transport):

    def __init__(self, beaver_config, file_config):
        super(UdpTransport, self).__init__(beaver_config, file_config)

        self.sock = socket.socket(socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP
        self.udp_host = beaver_config.get('udp_host')
        self.udp_port = int(beaver_config.get('udp_port'))

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for line in lines:
            formatted = self.format(filename, timestamp, line)
            self.sock.sendto(formatted, (self.udp_host, self.udp_port))
