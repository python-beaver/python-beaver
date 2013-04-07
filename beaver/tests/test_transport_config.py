# -*- coding: utf-8 -*-
import fakeredis
import logging
import mock
import unittest

import beaver
from beaver.config import BeaverConfig, FileConfig
from beaver.transports import create_transport
from beaver.transports.base_transport import BaseTransport


class DummyTransport(BaseTransport):
    pass


with mock.patch('pika.adapters.BlockingConnection', autospec=True) as mock_pika:

    class TransportConfigTests(unittest.TestCase):
        def setUp(self):
            self.file_config = mock.Mock(spec=FileConfig)
            self.logger = logging.getLogger(__name__)

        def _get_config(self, **kwargs):
            return BeaverConfig(mock.Mock(config=None, **kwargs))

        @mock.patch('pika.adapters.BlockingConnection', mock_pika)
        def test_builtin_rabbitmq(self):
            beaver_config = self._get_config(transport='rabbitmq')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.rabbitmq_transport.RabbitmqTransport)

        @mock.patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
        def test_builtin_redis(self):
            beaver_config = self._get_config(transport='redis')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.redis_transport.RedisTransport)

        def test_builtin_stdout(self):
            beaver_config = self._get_config(transport='stdout')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.stdout_transport.StdoutTransport)

        def test_builtin_udp(self):
            beaver_config = self._get_config(transport='udp')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.udp_transport.UdpTransport)

        def test_builtin_zmq(self):
            beaver_config = self._get_config(transport='zmq')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, beaver.zmq_transport.ZmqTransport)

        def test_custom_transport(self):
            beaver_config = self._get_config(transport='beaver.tests.test_transport_config.DummyTransport')
            transport = create_transport(beaver_config, self.file_config, logger=self.logger)
            self.assertIsInstance(transport, DummyTransport)
