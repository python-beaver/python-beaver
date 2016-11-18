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

from moto import mock_kinesis
import boto.kinesis

class KinesisTests(unittest.TestCase):

    @mock_kinesis
    def _create_streams(self):
        conn = boto.kinesis.connect_to_region("us-east-1")
        conn.create_stream("stream1", 1)
        conn.create_stream("stream2", 1)

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)

        empty_conf = tempfile.NamedTemporaryFile(delete=True)
        cls.beaver_config = BeaverConfig(mock.Mock(config=empty_conf.name))
        cls.beaver_config.set('transport', 'kinesis')
        cls.beaver_config.set('logstash_version', 1)

        output_file = Fixture.download_official_distribution()
        Fixture.extract_distribution(output_file)

    @mock_kinesis
    def test_kinesis_default_auth_profile(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_profile_name', None)
        self.beaver_config.set('kinesis_aws_access_key', None)
        self.beaver_config.set('kinesis_aws_secret_key', None)
        self.beaver_config.set('kinesis_aws_stream', 'stream1')

        transport = create_transport(self.beaver_config, logger=self.logger)

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)
        transport.interrupt()

    @mock_kinesis
    def test_kinesis_auth_profile(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_profile_name', 'beaver_stream')
        self.beaver_config.set('kinesis_aws_access_key', None)
        self.beaver_config.set('kinesis_aws_secret_key', None)
        self.beaver_config.set('kinesis_aws_stream', 'stream1')

        transport = create_transport(self.beaver_config, logger=self.logger)

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)

    @mock_kinesis
    def test_kinesis_auth_key(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_profile_name', None)
        self.beaver_config.set('kinesis_aws_access_key', 'beaver_test_key')
        self.beaver_config.set('kinesis_aws_secret_key', 'beaver_test_secret')
        self.beaver_config.set('kinesis_aws_stream', 'stream1')

        transport = create_transport(self.beaver_config, logger=self.logger)

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)
        transport.interrupt()

    @mock_kinesis
    def test_kinesis_auth_account_id(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_stream_owner_acct_id', 'abc123')
        self.beaver_config.set('kinesis_aws_profile_name', None)
        self.beaver_config.set('kinesis_aws_access_key', 'beaver_test_key')
        self.beaver_config.set('kinesis_aws_secret_key', 'beaver_test_secret')
        self.beaver_config.set('kinesis_aws_stream', 'stream1')

        transport = create_transport(self.beaver_config, logger=self.logger)

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)
        transport.interrupt()

    @mock_kinesis
    def test_kinesis_send_stream(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_stream', 'stream1')
        self.beaver_config.set('kinesis_aws_profile_name', None)
        self.beaver_config.set('kinesis_aws_access_key', None)
        self.beaver_config.set('kinesis_aws_secret_key', None)
        self.beaver_config.set('kinesis_bulk_lines', False)

        transport = create_transport(self.beaver_config, logger=self.logger)
        mock_send_batch = mock.Mock()
        transport._send_message_batch = mock_send_batch

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)

        data = {}
        lines = []
        n=500
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
        self.assertTrue(transport.callback("test.log", **data))
        self.assertEqual(1, mock_send_batch.call_count)


    @mock_kinesis
    def test_kinesis_send_stream_with_record_count_cutoff(self):
        self._create_streams()
        self.beaver_config.set('kinesis_aws_stream', 'stream1')
        self.beaver_config.set('kinesis_aws_profile_name', None)
        self.beaver_config.set('kinesis_aws_access_key', None)
        self.beaver_config.set('kinesis_aws_secret_key', None)
        self.beaver_config.set('kinesis_bulk_lines', False)

        transport = create_transport(self.beaver_config, logger=self.logger)
        mock_send_batch = mock.Mock()
        transport._send_message_batch = mock_send_batch

        self.assertIsInstance(transport, beaver.transports.kinesis_transport.KinesisTransport)

        data = {}
        lines = []
        n = 501
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
        self.assertTrue(transport.callback("test.log", **data))
        self.assertEqual(2, mock_send_batch.call_count)
