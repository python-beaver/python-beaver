import os
import redis
import socket
import ujson as json
import urlparse
import zmq

from datetime import datetime


class Transport(object):

    def callback(self, filename, lines):
        return True

    def interrupt(self):
        return True

    def unhandled(self):
        return True


class ZmqTransport(Transport):

    def __init__(self):
        zeromq_address = os.environ.get("ZEROMQ_ADDRESS", "tcp://localhost:2120")
        zeromq_bind = os.environ.get("BIND", False)
        self.current_host = socket.gethostname()

        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUSH)

        if zeromq_bind:
            self.pub.bind(zeromq_address)
        else:
            self.pub.connect(zeromq_address)

    def callback(self, filename, lines):
        timestamp = datetime.now().isoformat()
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
            self.pub.send(json_msg)

    def interrupt(self):
        self.pub.close()
        self.ctx.term()

    def unhandled(self):
        return True


class StdoutTransport(Transport):

    def __init__(self):
        self.current_host = socket.gethostname()

    def callback(self, filename, lines):
        timestamp = datetime.now().isoformat()
        for line in lines:
            msg = line.strip(os.linesep)
            print "[{0}] [{1}] {2}".format(self.current_host, timestamp, msg)


class RedisTransport(Transport):

    def __init__(self):
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _url = urlparse.urlparse(redis_url, scheme="redis")
        _, _, _db = _url.path.rpartition("/")
        self.redis = redis.StrictRedis(_url.hostname, _url.port, int(_db))
        self.current_host = socket.gethostname()
        self.namespace = os.environ.get("REDIS_NAMESPACE", "logstash:beaver")

    def callback(self, filename, lines):
        timestamp = datetime.now().isoformat()
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
            self.redis.lpush(self.namespace, json_msg)
