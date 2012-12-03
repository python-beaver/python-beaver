
import unittest
import os

try:
    from beaver.zmq_transport import ZmqTransport
    skip = False
except ImportError, e:
    if e.message == "No module named zmq":
        skip = True


class Args():
    mode = ""


@unittest.skipIf(skip, "zmq not installed")
class ZmqTests(unittest.TestCase):

    def setUp(self):
        self.args = Args()
        self.args.mode = ""

    def test_pub(self):
        os.environ["ZEROMQ_ADDRESS"] = "tcp://localhost:2120"
        transport = ZmqTransport("/dev/null", self.args)
        transport.interrupt()
        assert not transport.zeromq_bind

    def test_bind(self):
        self.args.mode = "bind"
        os.environ["ZEROMQ_ADDRESS"] = "tcp://*:2120"
        transport = ZmqTransport("/dev/null", self.args)
        assert transport.zeromq_bind

