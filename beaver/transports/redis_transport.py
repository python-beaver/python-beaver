# -*- coding: utf-8 -*-
import redis
import traceback
import time
import urlparse

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RedisTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(RedisTransport, self).__init__(beaver_config, logger=logger)

        redis_url = beaver_config.get('redis_url')
        redis_password = beaver_config.get('redis_password')
        self._redis = redis.StrictRedis.from_url(redis_url, socket_timeout=10)
        self._redis_namespace = beaver_config.get('redis_namespace')
        self._is_valid = False

        self._connect()

    def _connect(self):
        wait = -1
        while True:
            wait += 1
            time.sleep(wait)
            if wait == 20:
                return False

            if wait > 0:
                self._logger.info("Retrying connection, attempt {0}".format(wait + 1))

            try:
                self._redis.ping()
                break
            except UserWarning:
                traceback.print_exc()
            except Exception:
                traceback.print_exc()

        self._is_valid = True
        self._pipeline = self._redis.pipeline(transaction=False)

    def reconnect(self):
        self._connect()

    def invalidate(self):
        """Invalidates the current transport"""
        super(RedisTransport, self).invalidate()
        self._redis.connection_pool.disconnect()
        return False

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            self._pipeline.rpush(
                self._redis_namespace,
                self.format(filename, line, timestamp, **kwargs)
            )

        try:
            self._pipeline.execute()
        except redis.exceptions.RedisError, e:
            traceback.print_exc()
            raise TransportException(str(e))
