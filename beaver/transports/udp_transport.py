# -*- coding: utf-8 -*-
import socket

from beaver.transports.base_transport import BaseTransport


class UdpTransport(BaseTransport):

    def __init__(self, beaver_config, file_config, logger=None):
        super(UdpTransport, self).__init__(beaver_config, file_config, logger=logger)

        self._sock = socket.socket(socket.AF_INET,  # Internet
                                   socket.SOCK_DGRAM)  # UDP
        self._address = (beaver_config.get('udp_host'), beaver_config.get('udp_port'))

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)

        for line in lines:
            formatted = self.format(filename, timestamp, line)
            self._sock.sendto(formatted, self._address)
