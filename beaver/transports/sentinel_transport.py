# -*- coding: utf-8 -*-
import redis
import traceback
import time
import socket
import ast

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException
from redis.sentinel import *


class SentinelTransport(BaseTransport):
    LIST_DATA_TYPE = 'list'
    CHANNEL_DATA_TYPE = 'channel'

    def __init__(self, beaver_config, logger=None):
        super(SentinelTransport, self).__init__(beaver_config, logger=logger)

        nodes = ast.literal_eval(beaver_config.get('sentinel_nodes'))
        self._namespace = beaver_config.get('redis_namespace')
        self._sentinel_master_name = beaver_config.get('sentinel_master_name')

        self._data_type = beaver_config.get('redis_data_type')
        if self._data_type not in [self.LIST_DATA_TYPE,
                                   self.CHANNEL_DATA_TYPE]:
            raise TransportException('Unknown Redis data type')

        self._sentinel = Sentinel(nodes, socket_timeout=0.1)
        self._get_master()

    def _get_master(self):
        if self._check_connection():
            self._master = self._sentinel.master_for(self._sentinel_master_name, socket_timeout=0.1)

    def _check_connection(self):
        """Checks if the given sentinel servers return the master"""

        try:
            if self._is_reachable():
                self._sentinel.discover_master(self._sentinel_master_name)
                return True
        except MasterNotFoundError:
            self._logger.warn('Master not found')
        except Exception, ex:
            self._logger.warn('Error in _check_connection(): %s' %traceback.print_exc())

        return False

    def _is_reachable(self):
        """Check if one of the given sentinel servers are reachable"""

        for node in nodes:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(node)
                return (result == 0)

        self._logger.warn('Cannot connect to one of the given sentinel servers')
        return False

    def reconnect(self):
        self._check_connections()

    def invalidate(self):
        """Invalidates the current transport and disconnects all redis connections"""

        super(SentinelTransport, self).invalidate()
        self._master.connection_pool.disconnect()
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

        pipeline = self._master.pipeline(transaction=False)

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
