# -*- coding: utf-8 -*-
import socket
import errno
import ssl
import time

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class TcpTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(TcpTransport, self).__init__(beaver_config, logger=logger)

        self._is_valid = False
        self._tcp_host = beaver_config.get('tcp_host')
        self._tcp_port = beaver_config.get('tcp_port')
        self._tcp_ssl_enabled = beaver_config.get('tcp_ssl_enabled')
        self._tcp_ssl_verify = beaver_config.get('tcp_ssl_verify')
        self._tcp_ssl_cacert = beaver_config.get('tcp_ssl_cacert')
        self._tcp_ssl_cert = beaver_config.get('tcp_ssl_cert')
        self._tcp_ssl_key = beaver_config.get('tcp_ssl_key')

        self._connect()

    def _connect(self):
        wait = -1
        self._logger.debug("SSL enabled for TCP transport? %s" % self._tcp_ssl_enabled)
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
                if self._tcp_ssl_enabled:
                    self._logger.debug("SSL wrapping")
                    self._sock = ssl.wrap_socket(self._sock,
                                                 keyfile=self._tcp_ssl_key,
                                                 certfile=self._tcp_ssl_cert,
                                                 ssl_version=ssl.PROTOCOL_TLSv1,
                                                 ca_certs=self._tcp_ssl_cacert)

            except Exception as e:
                self._logger.error("Exception caught in socket connection: " + str(e))
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

        try:
            for line in lines:
                self._sock.send(self.format(filename, line, timestamp, **kwargs) + "\n")
        except socket.error, e:
            self.invalidate()

            if isinstance(e.args, tuple):
                if e[0] == errno.EPIPE:
                    raise TransportException('Connection appears to have been lost')

            raise TransportException('Socket Error: %s', e.args)
        except Exception:
            self.invalidate()

            raise TransportException('Unspecified exception encountered')  # TRAP ALL THE THINGS!
