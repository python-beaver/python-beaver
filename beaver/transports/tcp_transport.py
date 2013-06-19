# -*- coding: utf-8 -*-
import socket
import time

from beaver.transports.base_transport import BaseTransport


class TcpTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(TcpTransport, self).__init__(beaver_config, logger=logger)

        self._is_valid = False
        self._tcp_host = beaver_config.get('tcp_host')
        self._tcp_port = beaver_config.get('tcp_port')

        self._connect()

    def _connect(self):
        wait = -1
        while True:
            wait += 1
            time.sleep(wait)
            
            if wait == 20:
                return False

            if wait > 0:
                self._logger.info("Retrying connection, attempt {0}".format(wait + 1))

            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
                self._sock.connect((self._tcp_host, int(self._tcp_port)))
            except Exception:
                pass
            else:
                self._logger.info("Connected")
                self._is_valid = True
                return True

    def reconnect(self):
        self._connect()

    def invalidate(self):
        """Invalidates the current transport"""
        super(TcpTransport, self).invalidate()
        self._sock.close()

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            self._sock.send(self.format(filename, line, timestamp, **kwargs) + "\n")
