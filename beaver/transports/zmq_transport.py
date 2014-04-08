# -*- coding: utf-8 -*-
import zmq

from beaver.transports.base_transport import BaseTransport


class ZmqTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(ZmqTransport, self).__init__(beaver_config, logger=logger)

        zeromq_addresses = beaver_config.get('zeromq_address')

        self._ctx = zmq.Context()
        if beaver_config.get('zeromq_pattern') == 'pub':
            self._pub = self._ctx.socket(zmq.PUB)
        else:
            self._pub = self._ctx.socket(zmq.PUSH)

        zeromq_hwm = beaver_config.get('zeromq_hwm')
        if zeromq_hwm:
            if hasattr(self._pub, 'HWM'): # ZeroMQ < 3
                self._pub.setsockopt(zmq.HWM, zeromq_hwm)
            else:
                self._pub.setsockopt(zmq.SNDHWM, zeromq_hwm)
                self._pub.setsockopt(zmq.RCVHWM, zeromq_hwm)

        if beaver_config.get('mode') == 'bind':
            for addr in zeromq_addresses:
                self._pub.bind(addr)
        else:
            for addr in zeromq_addresses:
                self._pub.connect(addr)

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            self._pub.send(self.format(filename, line, timestamp, **kwargs))

    def interrupt(self):
        self._pub.close()
        self._ctx.term()

    def unhandled(self):
        return True
