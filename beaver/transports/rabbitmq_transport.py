# -*- coding: utf-8 -*-
from Queue import Queue
import pika
import ssl
from threading import Thread
import time

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RabbitmqTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(RabbitmqTransport, self).__init__(beaver_config, logger=logger)

        self._rabbitmq_config = {}
        config_to_store = [
            'key', 'exchange', 'username', 'password', 'host', 'port', 'vhost',
            'queue', 'queue_durable', 'ha_queue', 'exchange_type', 'exchange_durable',
            'ssl', 'ssl_key', 'ssl_cert', 'ssl_cacert', 'timeout', 'delivery_mode', 'arguments'
        ]

        for key in config_to_store:
            self._rabbitmq_config[key] = beaver_config.get('rabbitmq_' + key)
        if self._rabbitmq_config['arguments']:
            self._rabbitmq_config['arguments'] = self.get_rabbitmq_args()
        if self._rabbitmq_config['ha_queue']:
            self._rabbitmq_config['arguments']['x-ha-policy'] = 'all'



        self._connection = None
        self._channel = None
        self._count = 0
        self._lines = Queue()
        self._connection_ok = False
        self._thread = None
        self._is_valid = True
        self._connect()

    def get_rabbitmq_args(self):
        res = {}
        args = self._rabbitmq_config['arguments'].split(',')
        for x in args:
            k, v = x.split(':')
            try:
                # convert str to int if not a str
                v = int(v)
            except ValueError:
                pass  # is a str, not an int
            res[k] = v
        return res


    def _on_connection_open(self,connection):
        self._logger.debug("RabbitMQ: Connection Created")
        self._channel = connection.channel(self._on_channel_open)

    def _on_channel_open(self,unused):
        self._logger.debug("RabbitMQ: Channel Created")
        self._channel.exchange_declare(self._on_exchange_declareok,
                                       exchange=self._rabbitmq_config['exchange'],
                                       exchange_type=self._rabbitmq_config['exchange_type'],
                                       durable=self._rabbitmq_config['exchange_durable'])

    def _on_exchange_declareok(self,unused):
        self._logger.debug("RabbitMQ: Exchange Declared")
        self._channel.queue_declare(self._on_queue_declareok,
                                    queue=self._rabbitmq_config['queue'],
                                    durable=self._rabbitmq_config['queue_durable'],
                                    arguments=self._rabbitmq_config['arguments'])

    def _on_queue_declareok(self,unused):
        self._logger.debug("RabbitMQ: Queue Declared")
        self._channel.queue_bind(self._on_bindok,
                                 exchange=self._rabbitmq_config['exchange'],
                                 queue=self._rabbitmq_config['queue'],
                                 routing_key=self._rabbitmq_config['key'])

    def _on_bindok(self,unused):
        self._logger.info("RabbitMQ: Connection OK.")
        self._connection_ok = True
        self._logger.debug("RabbitMQ: Scheduling regular message transport.")
        self._connection.add_timeout(1, self._publish_message)

    def _publish_message(self):
        self._logger.debug("RabbitMQ: Looking for messages to transport...")
        while self._connection_ok and not self._lines.empty():
            line = self._lines.get()
            if self._count == 10000:
                self._logger.debug("RabbitMQ: Transport queue size: %s", self._lines.qsize())
                self._count = 0
            else:
                self._count += 1
            self._channel.basic_publish(
                exchange=self._rabbitmq_config['exchange'],
                routing_key=self._rabbitmq_config['key'],
                body=line,
                properties=pika.BasicProperties(
                    content_type='text/json',
                    delivery_mode=self._rabbitmq_config['delivery_mode']
                ))
        if self._connection_ok:
            self._logger.debug("RabbitMQ: No messages to transport. Sleeping.")
            self._connection.add_timeout(1, self._publish_message)
        else:
            self._logger.info('RabbitMQ: Message publisher stopped.')

    def _on_connection_open_error(self, non_used_connection=None, error=None):
        self._connection_ok = False
        self._logger.error('RabbitMQ: Could not open connection: %s', error)

    def _on_connection_closed(self, connection, reply_code, reply_text):
        self._connection_ok = False
        self._logger.warning('RabbitMQ: Connection closed: %s %s', reply_code, reply_text)

    def reconnect(self):
        self._logger.debug("RabbitMQ: Reconnecting...")
        self.interrupt()

        self._thread = Thread(target=self._connection_start)
        self._thread.start()
        while self._thread.is_alive() and not self._connection_ok:
            time.sleep(1)
        if self._connection_ok:
            self._is_valid = True
            self._logger.info('RabbitMQ: Reconnect successful.')
        else:
            self._logger.warning('RabbitMQ: Reconnect failed!')
            self.interrupt()

    def _connection_start(self):
        self._logger.debug("RabbitMQ: Connecting...")
        try:
            self._connection_ok = False
            self._connection = pika.adapters.SelectConnection(
                parameters=self._parameters,
                on_open_callback=self._on_connection_open,
                on_open_error_callback=self._on_connection_open_error,
                on_close_callback=self._on_connection_closed
            )
            if not self._connection.is_closed:
                self._connection.ioloop.start()
        except Exception as e:
            self._logger.error('RabbitMQ: Failed to connect: %s', e)

    def _connect(self):
        credentials = pika.PlainCredentials(
            self._rabbitmq_config['username'],
            self._rabbitmq_config['password']
        )
        ssl_options = {
            'keyfile': self._rabbitmq_config['ssl_key'],
            'certfile': self._rabbitmq_config['ssl_cert'],
            'ca_certs': self._rabbitmq_config['ssl_cacert'],
            'ssl_version': ssl.PROTOCOL_TLSv1
        }
        self._parameters = pika.connection.ConnectionParameters(
            credentials=credentials,
            host=self._rabbitmq_config['host'],
            port=self._rabbitmq_config['port'],
            ssl=self._rabbitmq_config['ssl'],
            ssl_options=ssl_options,
            virtual_host=self._rabbitmq_config['vhost'],
            socket_timeout=self._rabbitmq_config['timeout']
        )
        self._thread = Thread(target=self._connection_start)
        self._thread.start()

    def callback(self, filename, lines, **kwargs):
        if not self._connection_ok:
            raise TransportException('RabbitMQ: Not connected or connection not OK')
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']
        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    body = self.format(filename, line, timestamp, **kwargs)
                    self._lines.put(body)
            except UserWarning:
                raise TransportException('Connection appears to have been lost')
            except Exception as e:
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')

    def interrupt(self):
        self._connection_ok = False
        if self._connection:
            self._connection.close()
            self._connection = None
        if self._thread:
            self._thread.join()
            self._thread = None

    def unhandled(self):
        return True
