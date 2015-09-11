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
            'ssl', 'ssl_key', 'ssl_cert', 'ssl_cacert', 'timeout', 'delivery_mode'
        ]

        for key in config_to_store:
            self._rabbitmq_config[key] = beaver_config.get('rabbitmq_' + key)

        self._connection = None
        self._channel = None
        self._count = 0
        self._lines = Queue()
        self._connect()

    def _on_connection_open(self,connection):
        self._logger.debug("connection created")
        self._channel = connection.channel(self._on_channel_open)

    def _on_channel_open(self,unused):
        self._logger.debug("Channel Created")
        self._channel.exchange_declare(self._on_exchange_declareok,
                                       exchange=self._rabbitmq_config['exchange'],
                                       exchange_type=self._rabbitmq_config['exchange_type'],
                                       durable=self._rabbitmq_config['exchange_durable'])

    def _on_exchange_declareok(self,unused):
        self._logger.debug("Exchange Declared")
        self._channel.queue_declare(self._on_queue_declareok,
                                    queue=self._rabbitmq_config['queue'],
                                    durable=self._rabbitmq_config['queue_durable'],
                                    arguments={'x-ha-policy': 'all'} if self._rabbitmq_config['ha_queue'] else {})

    def _on_queue_declareok(self,unused):
        self._logger.debug("Queue Declared")
        self._channel.queue_bind(self._on_bindok,
                                 exchange=self._rabbitmq_config['exchange'],
                                 queue=self._rabbitmq_config['queue'],
                                 routing_key=self._rabbitmq_config['key'])

    def _on_bindok(self,unused):
        self._logger.debug("Exchange to Queue Bind OK")
        self._is_valid = True;
        self._logger.debug("Scheduling next message for %0.1f seconds",1)
        self._connection.add_timeout(1,self._publish_message)


    def _publish_message(self):
        while True:
            self._count += 0
            if self._lines.not_empty:
                line = self._lines.get()
                if self._count == 10000:
                    self._logger.debug("RabbitMQ transport queue size: %s" % (self._lines.qsize(), ))
                    self._count = 0
                else:
                    self._count += 1
                if self._channel != None:
                    self._channel.basic_publish(
                            exchange=self._rabbitmq_config['exchange'],
                            routing_key=self._rabbitmq_config['key'],
                            body=line,
                            properties=pika.BasicProperties(
                                content_type='text/json',
                                delivery_mode=self._rabbitmq_config['delivery_mode']
                            ))
            else:
                self._logger.debug("RabbitMQ transport queue is empty, sleeping for 1 second.")
                time.sleep(1)



    def _on_connection_open_error(self,non_used_connection=None,error=None):
        self._logger.debug("connection open error")
        if not error==None:
            self._logger.error(error)

    def _on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if hasattr(self._connection, '_closing'):
            closing = self._connection._closing
        elif hasattr(self._connection, 'is_closing'):
            closing = self._connection.is_closing
        else:
            raise NotImplementedError('Unsure how to check whether the connection is closing.')
        if closing:
            try:
                self._connection.ioloop.stop()
            except:
                pass
        else:
            self._logger.warning('RabbitMQ Connection closed, reopening in 1 seconds: (%s) %s',
                           reply_code, reply_text)
            time.sleep(1)
            self.reconnect()

    def reconnect(self):
        try:
            self._connection.ioloop.stop()
        except:
            pass
        self._connection_start()

    def _connection_start(self):
        self._logger.debug("Creating Connection")
        try:
            self._connection = pika.adapters.SelectConnection(parameters=self._parameters,on_open_callback=self._on_connection_open,on_open_error_callback=self._on_connection_open_error,on_close_callback=self._on_connection_closed,stop_ioloop_on_close=False)
        except Exception,e:
            self._logger.error("Failed Creating RabbitMQ connection")
            self._logger.error(e)
        self._logger.debug("Starting ioloop")
        self._connection.ioloop.start()

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
        self._parameters = pika.connection.ConnectionParameters(
            credentials=credentials,
            host=self._rabbitmq_config['host'],
            port=self._rabbitmq_config['port'],
            ssl=self._rabbitmq_config['ssl'],
            ssl_options=ssl_options,
            virtual_host=self._rabbitmq_config['vhost'],
            socket_timeout=self._rabbitmq_config['timeout']
        )
        Thread(target=self._connection_start).start()

    def callback(self, filename, lines, **kwargs):
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
                self._is_valid = False
                raise TransportException('Connection appears to have been lost')
            except Exception as e:
                self._is_valid = False
                try:
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')  # TRAP ALL THE THINGS!

    def interrupt(self):
        if self._connection:
            self._connection.close()

    def unhandled(self):
        return True
