# -*- coding: utf-8 -*-
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import mock
import tempfile
import logging

import beaver
from beaver.config import BeaverConfig
from beaver.transports import create_transport
from beaver.unicode_dammit import unicode_dammit

from fixtures import Fixture

from moto import mock_sqs
import boto.sqs

class SqsTests(unittest.TestCase):

    @mock_sqs
    def _create_queues(cls):
        conn = boto.sqs.connect_to_region("us-east-1")
        conn.create_queue("queue1")
        conn.create_queue("queue2")

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)

        empty_conf = tempfile.NamedTemporaryFile(delete=True)
        cls.beaver_config = BeaverConfig(mock.Mock(config=empty_conf.name))
        cls.beaver_config.set('transport', 'sqs')
        cls.beaver_config.set('logstash_version', 1)

        output_file = Fixture.download_official_distribution()
        Fixture.extract_distribution(output_file)

    @mock_sqs
    def test_sqs_default_auth_profile(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_aws_queue', 'queue1')

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_auth_profile(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_profile_name', 'beaver_queue')
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_aws_queue', 'queue1')

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)

    @mock_sqs
    def test_sqs_auth_key(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', 'beaver_test_key')
        cls.beaver_config.set('sqs_aws_secret_key', 'beaver_test_secret')
        cls.beaver_config.set('sqs_aws_queue', 'queue1')

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_auth_account_id(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue_owner_acct_id', 'abc123')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', 'beaver_test_key')
        cls.beaver_config.set('sqs_aws_secret_key', 'beaver_test_secret')
        cls.beaver_config.set('sqs_aws_queue', 'queue1')

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_single_queue(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_single_queue_bulklines(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', True)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_multi_queue(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1,queue2')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', False)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_multi_queue_bulklines(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1,queue2')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', True)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)
        transport.interrupt()

    @mock_sqs
    def test_sqs_send_single_queue(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', False)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)

        data = {}
        lines = []
        n=100
        for i in range(n):
            lines.append('log' + str(i) + '\n')
        new_lines = []
        for line in lines:
            message = unicode_dammit(line)
            if len(message) == 0:
                continue
            new_lines.append(message)
        data['lines'] = new_lines
        data['fields'] = []
        transport.callback("test.log", **data)

    @mock_sqs
    def test_sqs_send_multi_queue(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1,queue2')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', False)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)

        data = {}
        lines = []
        n=100
        for i in range(n):
            lines.append('log' + str(i) + '\n')
        new_lines = []
        for line in lines:
            message = unicode_dammit(line)
            if len(message) == 0:
                continue
            new_lines.append(message)
        data['lines'] = new_lines
        data['fields'] = []
        transport.callback("test.log", **data)

    @mock_sqs
    def test_sqs_send_single_queue_bulklines(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', True)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)

        data = {}
        lines = []
        n=100
        for i in range(n):
            lines.append('log' + str(i) + '\n')
        new_lines = []
        for line in lines:
            message = unicode_dammit(line)
            if len(message) == 0:
                continue
            new_lines.append(message)
        data['lines'] = new_lines
        data['fields'] = []
        transport.callback("test.log", **data)

    @mock_sqs
    def test_sqs_send_multi_queue_bulklines(cls):
	cls._create_queues()
        cls.beaver_config.set('sqs_aws_queue', 'queue1,queue2')
        cls.beaver_config.set('sqs_aws_profile_name', None)
        cls.beaver_config.set('sqs_aws_access_key', None)
        cls.beaver_config.set('sqs_aws_secret_key', None)
        cls.beaver_config.set('sqs_bulk_lines', True)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.sqs_transport.SqsTransport)

        data = {}
        lines = []
        n=100
        for i in range(n):
            lines.append('log' + str(i) + '\n')
        new_lines = []
        for line in lines:
            message = unicode_dammit(line)
            if len(message) == 0:
                continue
            new_lines.append(message)
        data['lines'] = new_lines
        data['fields'] = []
        transport.callback("test.log", **data)
