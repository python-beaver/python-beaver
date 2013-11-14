# -*- coding: utf-8 -*-
import pika
import ssl

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class RabbitmqTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(RabbitmqTransport, self).__init__(beaver_config, logger=logger)

        self._rabbitmq_config = {}
        config_to_store = [
            'key', 'exchange', 'username', 'password', 'host', 'port', 'vhost',
            'queue', 'queue_durable', 'ha_queue', 'exchange_type', 'exchange_durable',
            'ssl', 'ssl_key', 'ssl_cert', 'ssl_cacert'
        ]

        for key in config_to_store:
            self._rabbitmq_config[key] = beaver_config.get('rabbitmq_' + key)

        self._connection = None
        self._channel = None
        self._connect()

    def _connect(self):

        # Setup RabbitMQ connection
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
        parameters = pika.connection.ConnectionParameters(
            credentials=credentials,
            host=self._rabbitmq_config['host'],
            port=self._rabbitmq_config['port'],
            ssl=self._rabbitmq_config['ssl'],
            ssl_options=ssl_options,
            virtual_host=self._rabbitmq_config['vhost']
        )
        self._connection = pika.adapters.BlockingConnection(parameters)
        self._channel = self._connection.channel()

        # Declare RabbitMQ queue and bindings
        self._channel.queue_declare(
            queue=self._rabbitmq_config['queue'],
            durable=self._rabbitmq_config['queue_durable'],
            arguments={'x-ha-policy': 'all'} if self._rabbitmq_config['ha_queue'] else {}
        )
        self._channel.exchange_declare(
            exchange=self._rabbitmq_config['exchange'],
            exchange_type=self._rabbitmq_config['exchange_type'],
            durable=self._rabbitmq_config['exchange_durable']
        )
        self._channel.queue_bind(
            exchange=self._rabbitmq_config['exchange'],
            queue=self._rabbitmq_config['queue'],
            routing_key=self._rabbitmq_config['key']
        )

        self._is_valid = True;

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    self._channel.basic_publish(
                        exchange=self._rabbitmq_config['exchange'],
                        routing_key=self._rabbitmq_config['key'],
                        body=self.format(filename, line, timestamp, **kwargs),
                        properties=pika.BasicProperties(
                            content_type='text/json',
                            delivery_mode=1
                        )
                    )
            except UserWarning:
                self._is_valid = False
                raise TransportException('Connection appears to have been lost')
            except Exception, e:
                self._is_valid = False
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')  # TRAP ALL THE THINGS!

    def interrupt(self):
        if self._connection:
            self._connection.close()

    def reconnect(self):
        self._connect()

    def unhandled(self):
        return True
