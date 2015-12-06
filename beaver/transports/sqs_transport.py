# -*- coding: utf-8 -*-
import boto.sqs
import uuid

from boto.sqs.message import Message, RawMessage
from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException
from sys import getsizeof

class SqsTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(SqsTransport, self).__init__(beaver_config, logger=logger)

        self._access_key = beaver_config.get('sqs_aws_access_key')
        self._secret_key = beaver_config.get('sqs_aws_secret_key')
        self._profile = beaver_config.get('sqs_aws_profile_name')
        self._region = beaver_config.get('sqs_aws_region')
        self._queue_owner_acct_id = beaver_config.get('sqs_aws_queue_owner_acct_id')
        self._queue = beaver_config.get('sqs_aws_queue').split(',')
        self._bulk_lines = beaver_config.get('sqs_bulk_lines')

        try:
            if self._profile:
                self._connection = boto.sqs.connect_to_region(self._region,
                                                              profile_name=self._profile)
            elif self._access_key is None and self._secret_key is None:
                self._connection = boto.sqs.connect_to_region(self._region)
            else:
                self._connection = boto.sqs.connect_to_region(self._region,
                                                              aws_access_key_id=self._access_key,
                                                              aws_secret_access_key=self._secret_key)

            if self._connection is None:
                self._logger.warn('Unable to connect to AWS - check your AWS credentials')
                raise TransportException('Unable to connect to AWS - check your AWS credentials')

            self._queues = {}
            for queue in self._queue:
                self._logger.debug('Attempting to load SQS queue: {0}'.format(queue))
                if self._queue_owner_acct_id is None:
                    self._queues[queue] = self._connection.get_queue(queue)
                else:
                    self._queues[queue] = self._connection.get_queue(queue, 
                                                             owner_acct_id=self._queue_owner_acct_id)

                if self._queues[queue] is None:
                    raise TransportException('Unable to access queue with name {0}'.format(queue))

                self._logger.debug('Successfully loaded SQS queue: {0}'.format(queue))
        except Exception, e:
            raise TransportException(e.message)

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        if self._bulk_lines:
	    message_batch = ''
            message_count = 0
	else:
            message_batch = []

        message_batch_size = 0
        message_batch_size_max = 250000 # Max 256KiB but leave some headroom

        for line in lines:
            if self._bulk_lines:
               	m = self.format(filename, line, timestamp, **kwargs)
                message_size = getsizeof(m)
	    else:
                m = Message()
                m.set_body(self.format(filename, line, timestamp, **kwargs))
                message_size = len(m)

            if (message_size > message_batch_size_max):
                self._logger.debug('Dropping the message as it is too large to send ({0} bytes)'.format(message_size))
                continue

            # Check the new total size before adding a new message and don't try to send an empty batch
            if self._bulk_lines and (len(message_batch) > 0) and (((message_batch_size + message_size) >= message_batch_size_max)):
                self._logger.debug('Flushing {0} messages to SQS queue {1} bytes'.format(message_count, message_batch_size))
                self._send_message(message_batch)
                message_batch = ''
                message_count = 0
                message_batch_size = 0

            # SQS can only handle up to 10 messages in batch send and it can not exceed 256KiB (see above)
            elif (len(message_batch) > 0) and (((message_batch_size + message_size) >= message_batch_size_max) or (len(message_batch) == 10)):
                self._logger.debug('Flushing {0} messages to SQS queue {1} bytes'.format(len(message_batch), message_batch_size))
                self._send_message_batch(message_batch)
                message_batch = []
                message_batch_size = 0

            message_batch_size = message_batch_size + message_size

            if self._bulk_lines:
                message_batch += '{0},'.format(m)
                message_count += 1
            else:
                message_batch.append((uuid.uuid4(), self.format(filename, line, timestamp, **kwargs), 0))

        if len(message_batch) > 0:
            if self._bulk_lines:
                self._logger.debug('Flushing the last {0} messages to SQS queue {1} bytes'.format(message_count, message_batch_size))
                self._send_message(message_batch)
            else:
                self._logger.debug('Flushing the last {0} messages to SQS queue {1} bytes'.format(len(message_batch), message_batch_size))
                self._send_message_batch(message_batch)

        return True

    def _send_message(self, msg):
        for queue in self._queues:
            try:
                msg = '[{0}]'.format(msg.rstrip(','))
                m = RawMessage()
                m.set_body(msg)
                result = self._queues[queue].write(m)
                if not result:
                    self._logger.error('Error occurred sending message to SQS queue {0}. result: {1}'.format(
                        self._queue_name, result))
                    raise TransportException('Error occurred sending message to queue {0}'.format(self._queue_name))
            except Exception, e:
                self._logger.exception('Exception occurred sending message to SQS queue')
                raise TransportException(e.message)

    def _send_message_batch(self, message_batch):
        for queue in self._queues:
            try:
                self._logger.debug('Attempting to push batch message to SQS queue: {0}'.format(queue))
                result = self._queues[queue].write_batch(message_batch)
                if not result:
                    self._logger.error('Error occurred sending messages to SQS queue {0}. result: {1}'.format(
                        queue, result))
                    raise TransportException('Error occurred sending message to queue {0}'.format(queue))
                self._logger.debug('Successfully pushed batch message to SQS queue: {0}'.format(queue))
            except Exception, e:
                self._logger.exception('Exception occurred sending batch to SQS queue')
                raise TransportException(e.message)

    def interrupt(self):
        return True

    def unhandled(self):
        return True
