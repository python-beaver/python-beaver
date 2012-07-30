import os
import redis
import ujson as json
import socket
import urlparse

from transport import *


class RedisTransport(Transport):

    def __init__(self):
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _url = urlparse.urlparse(redis_url, scheme="redis")
        _, _, _db = _url.path.rpartition("/")
        self.redis = redis.StrictRedis(_url.hostname, _url.port, int(_db))
        self.current_host = socket.gethostname()
        self.namespace = os.environ.get("NAMESPACE", "logstash:beaver")

    def callback(self, filename, lines):
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://%s%s" % (self.current_host, filename),
                '@source_host': self.current_host,
                '@message': line.rstrip(os.linesep),
                '@source_path': filename
            })
            self.redis.lpush(self.namespace, json_msg)
