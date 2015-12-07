# -*- coding: utf-8 -*-
import redis
import traceback
import time

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RedisTransport(BaseTransport):
    LIST_DATA_TYPE = 'list'
    CHANNEL_DATA_TYPE = 'channel'

    def __init__(self, beaver_config, logger=None):
        super(RedisTransport, self).__init__(beaver_config, logger=logger)

        urls = beaver_config.get('redis_url')
        self._servers = []
        for url in urls.split(','):
            self._servers.append(
                {
                     'redis': redis.StrictRedis.from_url(url, socket_timeout=10),
                     'url': url,
                     'down_until': 0
                }
            )

        self._namespace = beaver_config.get('redis_namespace')
        self._current_server_index = 0

        self._data_type = beaver_config.get('redis_data_type')
        if self._data_type not in [self.LIST_DATA_TYPE,
                                   self.CHANNEL_DATA_TYPE]:
            raise TransportException('Unknown Redis data type')

        self._check_connections()

    def _check_connections(self):
        """Checks if all configured redis servers are reachable"""

        for server in self._servers:
            if self._is_reachable(server):
                server['down_until'] = 0
            else:
                server['down_until'] = time.time() + 5

    def _is_reachable(self, server):
        """Checks if the given redis server is reachable"""

        try:
            server['redis'].ping()
            return True
        except UserWarning:
            self._logger.warn('Cannot reach redis server: ' + server['url'])
        except Exception:
            self._logger.warn('Cannot reach redis server: ' + server['url'])

        return False

    def reconnect(self):
        self._check_connections()

    def invalidate(self):
        """Invalidates the current transport and disconnects all redis connections"""

        super(RedisTransport, self).invalidate()
        for server in self._servers:
            server['redis'].connection_pool.disconnect()
        return False

    def callback(self, filename, lines, **kwargs):
        """Sends log lines to redis servers"""

        self._logger.debug('Redis transport called')

        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        namespaces = self._beaver_config.get_field('redis_namespace', filename)
        if not namespaces:
            namespaces = self._namespace
        namespaces = namespaces.split(",")

        self._logger.debug('Got namespaces: '.join(namespaces))

        data_type = self._data_type
        self._logger.debug('Got data type: ' + data_type)

        server = self._get_next_server()
        self._logger.debug('Got redis server: ' + server['url'])

        pipeline = server['redis'].pipeline(transaction=False)

        callback_map = {
            self.LIST_DATA_TYPE: pipeline.rpush,
            self.CHANNEL_DATA_TYPE: pipeline.publish,
        }
        callback_method = callback_map[data_type]

        for line in lines:
            for namespace in namespaces:
                callback_method(
                    namespace.strip(),
                    self.format(filename, line, timestamp, **kwargs)
                )

        try:
            pipeline.execute()
        except redis.exceptions.RedisError, exception:
            self._logger.warn('Cannot push lines to redis server: ' + server['url'])
            raise TransportException(exception)

    def _get_next_server(self):
        """Returns a valid redis server or raises a TransportException"""

        current_try = 0
        max_tries = len(self._servers)

        while current_try < max_tries:

            server_index = self._raise_server_index()
            server = self._servers[server_index]
            down_until = server['down_until']

            self._logger.debug('Checking server ' + str(current_try + 1) + '/' + str(max_tries) + ': ' + server['url'])

            if down_until == 0:
                self._logger.debug('Elected server: ' + server['url'])
                return server

            if down_until < time.time():
                if self._is_reachable(server):
                    server['down_until'] = 0
                    self._logger.debug('Elected server: ' + server['url'])

                    return server
                else:
                    self._logger.debug('Server still unavailable: ' + server['url'])
                    server['down_until'] = time.time() + 5

            current_try += 1

        raise TransportException('Cannot reach any redis server')

    def _raise_server_index(self):
        """Round robin magic: Raises the current redis server index and returns it"""

        self._current_server_index = (self._current_server_index + 1) % len(self._servers)

        return self._current_server_index


    def valid(self):
        """Returns whether or not the transport can send data to any redis server"""

        valid_servers = 0
        for server in self._servers:
            if server['down_until'] <= time.time():
                valid_servers += 1

        return valid_servers > 0
