# -*- coding: utf-8 -*-
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import socket
import mock
import tempfile
import logging
import httpretty

import beaver
from beaver.config import BeaverConfig
from beaver.transports import create_transport
from beaver.transports.exception import TransportException

from beaver.unicode_dammit import unicode_dammit

from fixtures import Fixture, ZookeeperFixture, KafkaFixture

from beaver.transports.monascalog_transport import MonascalogTransport
from beaver.transports.monascalog_transport import MonascaLogRecord
from beaver.transports.monascalog_transport import MonascaLogger


logging.basicConfig(loglevel=logging.DEBUG)
logger = logging.getLogger("test")

class MonascaLogRecordTest(unittest.TestCase):

    @classmethod
    def SetUpClass(cls):
        pass

    @classmethod
    def TearDownClass(cls):
        pass

    def test_plain_text_format(self):
        # test a simple plain text log
        record = MonascaLogRecord("simple log line")
        self.assertEqual(record.is_json(), False)

    def test_json_format(self):
        # test a simple json log line
        record = MonascaLogRecord('{"message": "simple log line", "type": "keystone"}',
                                  is_json=True,
                                  logger=logger)
        self.assertEqual(record.is_json(), True)

        # get the json payload and make sure it is formatted in a way log api
        # expects it
        json_line = record.to_json()
        self.assertIn("dimensions", json_line.keys())
        self.assertIn("type", json_line["dimensions"].keys())
        self.assertEqual(json_line["message"], "simple log line")
        self.assertEqual(record.is_valid(), True)


class MonascaLoggerTest(unittest.TestCase):

    @classmethod
    def SetUpClass(cls):
        pass

    @classmethod
    def TearDownClass(cls):
        pass

    def test_construction(self):
        m_logger = MonascaLogger(logger=logger)
        self.assertIsInstance(m_logger, MonascaLogger)
        self.assertEqual(m_logger._enable_batching, True)

# using localhost to prevent proxy issues with httpretty
#LOG_URL = "http://www.logapi.com:5607/v3.0/logs"
LOG_URL = "http://localhost:5607/v3.0/logs"

class MonascalogTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(__name__)

        empty_conf = tempfile.NamedTemporaryFile(delete=True)
        cls.beaver_config = BeaverConfig(mock.Mock(config=empty_conf.name))
        cls.server_host = "localhost"
        cls.server_port = 5607
        cls.keystone_auth_url = "https://www.keystone.com:5000/v3.0/auth/tokens"
        cls.keystone_user = "logger"
        cls.keystone_password = "logger"
        cls.keystone_project_name = "logger"
        cls.keystone_domain_name = "logger"
        cls.log_requests = []
        cls.hostname = socket.gethostname()

    @classmethod
    def tearDownClass(cls):
        pass

    @httpretty.activate
    @mock.patch('beaver.transports.monascalog_transport.KeystoneClientHelper.get_token_and_log_url', return_value=("1234",LOG_URL))
    def test_monascalog(cls, token_mock):

        # dynamic callback to verify the log messages sent by the transport
        def request_callback(request, uri, headers):
            cls.log_requests.append(request.parsed_body)
            return (204, headers, "created")

        # fake the first get call that is used for checking connection
        httpretty.register_uri(httpretty.GET, LOG_URL, status=405, body="Method Not Allowed")
        httpretty.register_uri(httpretty.POST, LOG_URL, status=204, body="Created")
        cls.beaver_config.set('transport', 'monascalog')
        cls.beaver_config.set('logstash_version', 1)
        #cls.beaver_config.set('monascalog_hosts',  "{}:{}".format(cls.server_host, cls.server_port))
        cls.beaver_config.set('monascalog_max_retries', 3)
        cls.beaver_config.set('monascalog_auth_url', cls.keystone_auth_url)
        cls.beaver_config.set('monascalog_user_name', cls.keystone_user)
        cls.beaver_config.set('monascalog_password', cls.keystone_password)
        cls.beaver_config.set('monascalog_project_name', cls.keystone_project_name)
        cls.beaver_config.set('monascalog_domain_name', cls.keystone_domain_name)

        transport = create_transport(cls.beaver_config, logger=cls.logger)

        cls.assertIsInstance(transport, beaver.transports.monascalog_transport.MonascalogTransport)
        cls.assertEqual(transport.valid(), True)

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
        cls.assertEqual(transport.callback("test.log", **data), True)

        # Fake a log api failure
        httpretty.reset()
        httpretty.register_uri(httpretty.POST, LOG_URL, status=500, body="Internal Server Error")
        cls.assertRaises(TransportException, transport.callback, "test.log", **data)

        # simulate a single failure followed by success, to test if retry works
        httpretty.reset()
        httpretty.register_uri(httpretty.POST, LOG_URL, responses=[
                                                        httpretty.Response(status=503, body="Service Unavailable"),
                                                        httpretty.Response(status=204, body="Created")
                                                        ])
        cls.assertEqual(transport.callback("test.log", **data), True)

        # next, test if the logs made it to the server
        httpretty.reset()
        httpretty.register_uri(httpretty.POST, LOG_URL, body=request_callback)
        # clear logs from previous tests
        del cls.log_requests[:]
        cls.assertEqual(transport.callback("test.log", **data), True)
        cls._consume_messages(n)

        # repeat same test, but with batching turned off
        cls.beaver_config.set('monascalog_enable_batching', False)
        httpretty.reset()
        httpretty.register_uri(httpretty.POST, LOG_URL, body=request_callback)
        # fake the first get call that is used for checking connection
        httpretty.register_uri(httpretty.GET, LOG_URL, status=405, body="Method Not Allowed")
        transport = create_transport(cls.beaver_config, logger=cls.logger)
        # clear logs from previous tests
        del cls.log_requests[:]
        cls.assertEqual(transport.callback("test.log", **data), True)
        cls._consume_messages(n, batching=False)
        transport.interrupt()

    def _consume_messages(cls, number_of_messages, batching=True):
        messages = cls.log_requests
        for message in messages:
            cls.assertIn("dimensions", message)
            cls.assertIn("logs", message)
            cls.assertIsInstance(message["dimensions"], dict)
            dims = message["dimensions"]
            cls.assertEqual(dims["file"], "test.log")
            cls.assertEqual(dims["host"], cls.hostname)
            cls.assertIsInstance(message["logs"], list)
            for log in message["logs"]:
                cls.assertIn("message", log)
                if not log["message"]:
                    cls.fail("Log message is empty")
            #print(message)
        #print('\n')

        if not batching:
            cls.assertEqual(len(messages), number_of_messages)
        else:
            msg = messages[0]
            cls.assertEqual(len(msg["logs"]), number_of_messages)
