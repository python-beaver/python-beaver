import datetime
import redis
import time
import urlparse

import beaver.transport


class RedisTransport(beaver.transport.Transport):

    def __init__(self, beaver_config, file_config):
        super(RedisTransport, self).__init__(beaver_config, file_config)

        redis_url = beaver_config.get('redis_url')
        _url = urlparse.urlparse(redis_url, scheme="redis")
        _, _, _db = _url.path.rpartition("/")

        self.redis = redis.StrictRedis(host=_url.hostname, port=_url.port, db=int(_db), socket_timeout=10)
        self.redis_namespace = beaver_config.get('redis_namespace')

        wait = 0
        while 1:
            if wait == 20:
                break

            time.sleep(0.1)
            wait += 1
            try:
                self.redis.ping()
                break
            except redis.exceptions.ConnectionError:
                pass

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        for line in lines:
            self.redis.rpush(
                self.redis_namespace,
                self.format(filename, timestamp, line)
            )
