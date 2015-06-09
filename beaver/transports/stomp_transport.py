# -*- coding: utf-8 -*-
import stomp

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class StompTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        """
        Mosquitto client initilization. Once this this transport is initialized
        it has invoked a connection to the server
        """
        super(StompTransport, self).__init__(beaver_config, logger=logger)

        self.createConnection(beaver_config)
        self.logger = logger

 
    def callback(self, filename, lines, **kwargs):
        """publishes lines one by one to the given topic"""
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']
        

        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    m = self.format(filename, line, timestamp, **kwargs)
                    self.logger.debug("Sending message " + m)
                    self.conn.send(destination=self.queue, body=m)    

            except Exception, e:
                self.logger.error(e)
                try:
                    raise TransportException(e)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')

    def createConnection(self, beaver_config):
        self.host = beaver_config.get('stomp_host')
        self.port = int(beaver_config.get('stomp_port'))
        self.userName = beaver_config.get('stomp_user', None)
        self.password = beaver_config.get('stomp_password', None)
        self.queue = beaver_config.get('stomp_queue')
        self.stompConnect()

    def stompConnect(self):
        try:
          host_and_ports = (self.host, self.port)
          self.conn = stomp.Connection([host_and_ports]);
          self.conn.start()
          self.conn.connect(self.userName, self.password)
        except stomp.exception.NotConnectedException, e:
            try:
                raise TransportException(e.strerror)
            except AttributeError:
                raise TransportException('Unspecified exception encountered')

    def reconnect(self):
        """Allows reconnection from when a handled
        TransportException is thrown"""
        try:
            self.conn.close()
        except Exception,e:
            self.logger.warn(e)

        self.createConnection()

        return True

    def interrupt(self):
        if self.conn:
            self.conn.close()

    def unhandled(self):
        return True
