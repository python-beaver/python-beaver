# -*- coding: utf-8 -*-
import redis
import traceback
import time
import urlparse
import random

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RedisTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(RedisTransport, self).__init__(beaver_config, logger=logger)

        redis_url = beaver_config.get('redis_url')
        self._redis_password = beaver_config.get('redis_password')
        self._redishosts = str(redis_url).split(',')
        self._current_redis = 0
        self._redis_url = self._redishosts[self._current_redis]
        self._redis = redis.StrictRedis.from_url(self._redis_url, socket_timeout=10)
        self._redis_namespace = beaver_config.get('redis_namespace')
        self._is_valid = False
        self._blacklisted_hosts = set()

        self._connect()

    def _pick_connection(self):
        """Picks up a random redis url for connection."""
        for self._current_redis in xrange(self._current_redis + 1, len(self._redishosts)):
            host = self._redishosts[self._current_redis]
            if host not in self._blacklisted_hosts:
                break
        else:
            self._logger.info('No more healthy hosts, retry with previously blacklisted')
            random.shuffle(self._redishosts)
            self._blacklisted_hosts.clear()
            self._current_redis = 0
            host = self._redishosts[self._current_redis]

        self._redis_url = host
        self._redis = redis.StrictRedis.from_url(self._redis_url, socket_timeout=10)
        self._logger.info('Selected connection: %s', self._redis_url)

    def _blacklist_connection(self):
        """Marks the current redis host we're trying to use as blacklisted.

           Blacklisted hosts will get another chance to be elected once there
           will be no more healthy hosts."""
        # FIXME: Enhance this naive strategy.
        self._logger.info('Blacklisting %s for a while', self._redis_url)
        self._blacklisted_hosts.add(self._redis_url)

    def _connect(self):
        wait = -1
        while True:
            wait += 1
            time.sleep(wait)
            if wait == 20:
                return False

            if wait > 0:
                self._logger.info("Retrying connection, attempt {0}".format(wait + 1))
                self._blacklist_connection()
                self._pick_connection()

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

        rn = self._beaver_config.get_field('redis_namespace', filename)
        if not rn:
            rn = self._redis_namespace
        self._logger.debug('redis_namespace: '+rn)

        for line in lines:
            self._pipeline.rpush(
                rn,
                self.format(filename, line, timestamp, **kwargs)
            )

        try:
            self._pipeline.execute()
        except redis.exceptions.RedisError, e:
            traceback.print_exc()
            raise TransportException(str(e))
