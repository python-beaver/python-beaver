import os
import redis
import simplejson as json
import socket
import urlparse

from transport import *

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
_url = urlparse.urlparse(REDIS_URL, scheme="redis")
_, _, _db = _url.path.rpartition("/")
REDIS = redis.StrictRedis(_url.hostname, _url.port, int(_db))
CURRENT_HOST = socket.gethostname()


class RedisTransport(Transport):

    def callback(self, filename, lines):
        for line in lines:
            json_msg = json.dumps({
                '@source': "file://%s%s" % (CURRENT_HOST, filename),
                '@source_host': CURRENT_HOST,
                '@message': line.rstrip(os.linesep),
                '@source_path': filename
            })
            REDIS.lpush(json_msg)
