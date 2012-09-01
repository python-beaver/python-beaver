import datetime
import os
import redis
import urlparse

import beaver.transport


class RedisTransport(beaver.transport.Transport):

    def __init__(self, configfile):
        super(RedisTransport, self).__init__(configfile)

        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _url = urlparse.urlparse(redis_url, scheme="redis")
        _, _, _db = _url.path.rpartition("/")

        self.redis = redis.StrictRedis(host=_url.hostname, port=_url.port, db=int(_db), socket_timeout=10)
        self.redis_namespace = os.environ.get("REDIS_NAMESPACE", "logstash:beaver")

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().isoformat()
        for line in lines:
            self.redis.lpush(
                self.redis_namespace,
                self.format(filename, timestamp, line)
            )
