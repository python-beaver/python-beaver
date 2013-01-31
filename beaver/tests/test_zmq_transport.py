import mock
import os
import unittest

from beaver.config import BeaverConfig, FileConfig

try:
    from beaver.zmq_transport import ZmqTransport
    skip = False
except ImportError, e:
    if e.message == "No module named zmq":
        skip = True


@unittest.skipIf(skip, "zmq not installed")
class ZmqTests(unittest.TestCase):

    def setUp(self):
        self.file_config = mock.Mock(spec=FileConfig)
        self.beaver_config = BeaverConfig(mock.Mock(config=None))

    def test_pub(self):
        os.environ["ZEROMQ_ADDRESS"] = "tcp://localhost:2120"
        transport = ZmqTransport(self.beaver_config, self.file_config)
        transport.interrupt()
        #assert not transport.zeromq_bind

    def test_bind(self):
        self.beaver_config.mode = "bind"
        os.environ["ZEROMQ_ADDRESS"] = "tcp://*:2120"
        transport = ZmqTransport(self.beaver_config, self.file_config)
        #assert transport.zeromq_bind

