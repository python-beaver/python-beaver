# -*- coding: utf-8 -*-
import mock
import unittest
import tempfile
import logging


import beaver
from beaver.config import BeaverConfig
from beaver.transports import create_transport

from beaver.unicode_dammit import unicode_dammit

from fixtures import Fixture, ZookeeperFixture, KafkaFixture

try:
    from beaver.transports.kafka_transport import KafkaTransport
    skip = False
except ImportError, e:
    if e.message == 'No module named kafka':
        skip = True
    else:
        raise


@unittest.skipIf(skip, 'kafka not installed')
class KafkaTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)

        empty_conf = tempfile.NamedTemporaryFile(delete=True)
        cls.beaver_config = BeaverConfig(mock.Mock(config=empty_conf.name))

        output_file = Fixture.download_official_distribution()
        Fixture.extract_distribution(output_file)
        cls.zk = ZookeeperFixture.instance()
        cls.server = KafkaFixture.instance(0, cls.zk.host, cls.zk.port)

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.zk.close()

    def test_builtin_kafka(cls):
        cls.beaver_config.set('transport', 'kafka')
        cls.beaver_config.set('logstash_version', 1)
        cls.beaver_config.set('kafka_hosts', cls.server.host + ":" + str(cls.server.port))

        transport = create_transport(cls.beaver_config, logger=cls.logger)
        data = {}
        lines = ['log1\n', 'log2\n']
        new_lines = []
        for line in lines:
            message = unicode_dammit(line)
            if len(message) == 0:
                continue
            new_lines.append(message)
        data['lines'] = new_lines
        data['fields'] = []
        transport.callback("test.log", **data)
        transport.interrupt()
        cls.assertIsInstance(transport, beaver.transports.kafka_transport.KafkaTransport)



