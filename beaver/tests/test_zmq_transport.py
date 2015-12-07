# -*- coding: utf-8 -*-
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import mock
import tempfile

from beaver.config import BeaverConfig

try:
    from beaver.transports.zmq_transport import ZmqTransport
    skip = False
except ImportError, e:
    if e.message == 'No module named zmq':
        skip = True
    else:
        raise


@unittest.skipIf(skip, 'zmq not installed')
class ZmqTests(unittest.TestCase):

    def setUp(self):
        empty_conf = tempfile.NamedTemporaryFile(delete=True)
        self.beaver_config = BeaverConfig(mock.Mock(config=empty_conf.name))

    def test_pub(self):
        self.beaver_config.set('zeromq_address', ['tcp://localhost:2120'])
        transport = ZmqTransport(self.beaver_config)
        transport.interrupt()
        #assert not transport.zeromq_bind

    def test_bind(self):
        self.beaver_config.set('zeromq_bind', 'bind')
        self.beaver_config.set('zeromq_address', ['tcp://localhost:2120'])
        ZmqTransport(self.beaver_config)
        #assert transport.zeromq_bind
