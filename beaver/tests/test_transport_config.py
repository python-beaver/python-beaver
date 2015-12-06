# -*- coding: utf-8 -*-
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import fakeredis
import logging
import mock
import tempfile

import beaver
from beaver.config import BeaverConfig
from beaver.transports import create_transport
from beaver.transports.base_transport import BaseTransport

try:
    from beaver.transports.zmq_transport import ZmqTransport
    zmqSkip = False
except ImportError, e:
    if e.message == 'No module named zmq':
        zmqSkip = True
    else:
        raise


class DummyTransport(BaseTransport):
    pass


with mock.patch('pika.adapters.SelectConnection') as mock_pika:

    class TransportConfigTests(unittest.TestCase):
        def setUp(self):
            self.logger = logging.getLogger(__name__)

        def _get_config(self, **kwargs):
            empty_conf = tempfile.NamedTemporaryFile(delete=True)
            return BeaverConfig(mock.Mock(config=empty_conf.name, **kwargs))

        @mock.patch('pika.adapters.SelectConnection', mock_pika)
        def test_builtin_rabbitmq(self):
            beaver_config = self._get_config(transport='rabbitmq')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.transports.rabbitmq_transport.RabbitmqTransport)

        @mock.patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
        def test_builtin_redis(self):
            beaver_config = self._get_config(transport='redis')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.transports.redis_transport.RedisTransport)

        def test_builtin_stdout(self):
            beaver_config = self._get_config(transport='stdout')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.transports.stdout_transport.StdoutTransport)

        def test_builtin_udp(self):
            beaver_config = self._get_config(transport='udp')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.transports.udp_transport.UdpTransport)

        @unittest.skipIf(zmqSkip, 'zmq not installed')
        def test_builtin_zmq(self):
            beaver_config = self._get_config(transport='zmq')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, ZmqTransport)

        def test_custom_transport(self):
            beaver_config = self._get_config(transport='beaver.tests.test_transport_config.DummyTransport')
            transport = create_transport(beaver_config, logger=self.logger)
            self.assertIsInstance(transport, DummyTransport)
