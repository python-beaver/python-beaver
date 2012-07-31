import os
import redis
import ujson as json
import socket
import urlparse
from datetime import datetime

from transport import Transport


class RedisTransport(Transport):

    def __init__(self):
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _url = urlparse.urlparse(redis_url, scheme="redis")
        _, _, _db = _url.path.rpartition("/")
        self.redis = redis.StrictRedis(_url.hostname, _url.port, int(_db))
        self.current_host = socket.gethostname()
        self.namespace = os.environ.get("REDIS_NAMESPACE", "logstash:beaver")
        print "waiting"

    def callback(self, filename, lines):
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': datetime.now().isoformat(),
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
            self.redis.lpush(self.namespace, json_msg)
