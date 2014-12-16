# -*- coding: utf-8 -*-
import boto.sqs
import uuid

from boto.sqs.message import Message

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class SqsTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(SqsTransport, self).__init__(beaver_config, logger=logger)

        self._access_key = beaver_config.get('sqs_aws_access_key')
        self._secret_key = beaver_config.get('sqs_aws_secret_key')
        self._region = beaver_config.get('sqs_aws_region')
        self._queue_name = beaver_config.get('sqs_aws_queue')

        try:
            if self._access_key is None and self._secret_key is None:
                self._connection = boto.sqs.connect_to_region(self._region)
            else:
                self._connection = boto.sqs.connect_to_region(self._region,
                                                              aws_access_key_id=self._access_key,
                                                              aws_secret_access_key=self._secret_key)

            if self._connection is None:
                self._logger.warn('Unable to connect to AWS - check your AWS credentials')
                raise TransportException('Unable to connect to AWS - check your AWS credentials')

            self._queue = self._connection.get_queue(self._queue_name)

            if self._queue is None:
                raise TransportException('Unable to access queue with name {0}'.format(self._queue_name))
        except Exception, e:
            raise TransportException(e.message)

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        message_batch_size = 0
        message_batch = []
        for line in lines:
            m = Message
            m.set_body(self.format(filename, line, timestamp, **kwargs))
            message_length = len(m)
            message_tuple = (uuid.uuid4(), self.format(filename, line, timestamp, **kwargs), 0)

            if message_length > 250000:
                self._logger.debug('Dropping message as it is too long to send ({0} bytes)'.format(message_length))
                continue

            if message_batch_size + message_length < 250000:
                message_batch.append(message_tuple)
            else:
                self._send_message_batch(message_batch)
                message_batch = []
                message_batch.append(message_tuple)
                continue

            # SQS can only handle up to 10 messages in batch send
            if len(message_batch) == 10:
                self._send_message_batch(message_batch)
                message_batch = []

        if len(message_batch) > 0:
            self._send_message_batch(message_batch)
        return True

    def _send_message_batch(self, message_batch):
        self._logger.debug('Flushing {0} messages to SQS queue'.format(len(message_batch)))
        try:
            result = self._queue.write_batch(message_batch)
            if not result:
                self._logger.error('Error occurred sending messages to SQS queue {0}. result: {1}'.format(
                    self._queue_name, result))
                raise TransportException('Error occurred sending message to queue {0}'.format(self._queue_name))
        except Exception, e:
            self._logger.exception('Exception occurred sending batch to SQS queue')
            raise TransportException(e.message)

    def interrupt(self):
        return True

    def unhandled(self):
        return True
