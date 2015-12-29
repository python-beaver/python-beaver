# -*- coding: utf-8 -*-
from kafka import SimpleProducer, KeyedProducer, KafkaClient, RoundRobinPartitioner

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException

class KafkaTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(KafkaTransport, self).__init__(beaver_config, logger=logger)

        self._kafka_config = {}
        config_to_store = [
            'client_id', 'hosts', 'async', 'topic', 'key',
            'ack_timeout', 'codec', 'batch_n', 'batch_t', 'round_robin'
        ]

        for key in config_to_store:
            self._kafka_config[key] = beaver_config.get('kafka_' + key)

        try:
            self._connect()
            self._client = KafkaClient(self._kafka_config['hosts'], self._kafka_config['client_id'])
            self._client.ensure_topic_exists(self._kafka_config['topic'])
            self._key = self._kafka_config['key']
            if self._key is None:
                self._prod = SimpleProducer(self._client, async=self._kafka_config['async'],
                                        req_acks=SimpleProducer.ACK_AFTER_LOCAL_WRITE,
                                        ack_timeout=self._kafka_config['ack_timeout'],
                                        codec=self._kafka_config['codec'],
                                        batch_send=True,
                                        batch_send_every_n=self._kafka_config['batch_n'],
                                        batch_send_every_t=self._kafka_config['batch_t'])
            else:
                partitioner = None
                if self._kafka_config['round_robin']:
                    partitioner = RoundRobinPartitioner
                self._prod = KeyedProducer(self._client, async=self._kafka_config['async'],
                                        partitioner=partitioner,
                                        req_acks=SimpleProducer.ACK_AFTER_LOCAL_WRITE,
                                        ack_timeout=self._kafka_config['ack_timeout'],
                                        codec=self._kafka_config['codec'],
                                        batch_send=True,
                                        batch_send_every_n=self._kafka_config['batch_n'],
                                        batch_send_every_t=self._kafka_config['batch_t'])

            self._is_valid = True

        except Exception, e:
            raise TransportException(e.message)

    def callback(self, filename, lines, **kwargs):
        """publishes lines one by one to the given topic"""
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    #produce message
                    if self._key is None:
                        response = self._prod.send_messages(self._kafka_config['topic'], self.format(filename, line, timestamp, **kwargs))
                    else:
                        response = self._prod.send_messages(self._kafka_config['topic'], self._key, self.format(filename, line, timestamp, **kwargs))

                    if response:
                        if response[0].error:
                            self._logger.info('message error: {0}'.format(response[0].error))
                            self._logger.info('message offset: {0}'.format(response[0].offset))

            except Exception as e:
                try:
                    self._logger.error('Exception caught sending message/s : ' + str(e))
                    raise TransportException(e.strerror)
                except AttributeError:
                    raise TransportException('Unspecified exception encountered')  # TRAP ALL THE THINGS!

    def _connect(self):
        try:
            self._client = KafkaClient(self._kafka_config['hosts'], self._kafka_config['client_id'])
            self._client.ensure_topic_exists(self._kafka_config['topic'])
        except Exception, e:
            raise TransportException(e.message)

    def reconnect(self):
            self._connect()

    def interrupt(self):
        if self._prod:
            self._prod.stop()
        if self._client:
            self._client.close()

    def unhandled(self):
        return True
