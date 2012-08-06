import datetime
import os
import redis
import ujson as json
import urlparse
import socket

import beaver.transport


class RedisTransport(beaver.transport.Transport):

    def __init__(self):
        _r = os.environ.get("REDIS_URL", None)
        print _r
        _url = urlparse.urlparse(_r, scheme="redis")
        _, _, _db = _url.path.rpartition("/")
        self.redis = redis.StrictRedis(_url.hostname, _url.port, int(_db))
        self.current_host = socket.gethostname()
        self.namespace = os.environ.get("REDIS_NAMESPACE", "logstash:beaver")

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
            self.redis.lpush(self.namespace, json_msg)
