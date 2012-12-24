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

        self._redis = redis.StrictRedis(host=_url.hostname, port=_url.port, db=int(_db), socket_timeout=10)
        self._redis_namespace = beaver_config.get('redis_namespace')

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
            self._redis.rpush(
                self._redis_namespace,
                self.format(filename, timestamp, line)
            )
