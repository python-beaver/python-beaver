import datetime
import os
import redis
import ujson as json
import urlparse
import socket

import beaver.transport


class RedisTransport(beaver.transport.Transport):

    def __init__(self):
        REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _url = urlparse.urlparse(REDIS_URL, scheme="redis")
        _, _, _db = _url.path.rpartition("/")
        self.redis = redis.StrictRedis(host=_url.hostname, port=_url.port, db=int(_db), socket_timeout=10)
        self.current_host = socket.gethostname()
        self.redis_namespace = os.environ.get("REDIS_NAMESPACE", "logstash:beaver")

    def callback(self, filename, lines):
        timestamp = datetime.datetime.now().isoformat()
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
            self.redis.lpush(self.redis_namespace, json_msg)
