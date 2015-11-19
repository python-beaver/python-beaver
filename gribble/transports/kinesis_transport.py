# -*- coding: utf-8 -*-
import boto.kinesis
import boto.kinesis.layer1
import uuid

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException


class KinesisTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(KinesisTransport, self).__init__(beaver_config, logger=logger)

        self._access_key = beaver_config.get('kinesis_aws_access_key')
        self._secret_key = beaver_config.get('kinesis_aws_secret_key')
        self._region = beaver_config.get('kinesis_aws_region')
        self._stream_name = beaver_config.get('kinesis_aws_stream')

        # self-imposed max batch size to minimize the number of records in a given call to Kinesis
        self._batch_size_max = beaver_config.get('kinesis_aws_batch_size_max', '512000')

        try:
            if self._access_key is None and self._secret_key is None:
                self._connection = boto.kinesis.connect_to_region(self._region)
            else:
                self._connection = boto.kinesis.connect_to_region(self._region,
                                                              aws_access_key_id=self._access_key,
                                                              aws_secret_access_key=self._secret_key)

            if self._connection is None:
                self._logger.warn('Unable to connect to AWS Kinesis - check your AWS credentials')
                raise TransportException('Unable to connect to AWS Kinesis - check your AWS credentials')

        except Exception, e:
            raise TransportException(e.message)


    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        message_batch = []
        message_batch_size = 0

        for line in lines:

            m = self.format(filename, line, timestamp, **kwargs)
            message_size = len(m)

            if (message_size > self._batch_size_max):
                self._logger.debug('Dropping the message as it is too large to send ({0} bytes)'.format(
                    message_size))
                continue

            # Check the self-enforced/declared batch size and flush before moving forward if we've eclipsed the max
            if (len(message_batch) > 0) and ((message_batch_size + message_size) >= self._batch_size_max):
                self._logger.debug('Flushing {0} messages to Kinesis stream {1} bytes'.format(
                    len(message_batch), message_batch_size))
                self._send_message_batch(message_batch)
                message_batch = []
                message_batch_size = 0

            message_batch_size = message_batch_size + message_size
            message_batch.append({'PartitionKey': uuid.uuid4().hex, 'Data': 
                self.format(filename, line, timestamp, **kwargs)})

        if len(message_batch) > 0:
            self._logger.debug('Flushing the last {0} messages to Kinesis stream {1} bytes'.format(
                len(message_batch), message_batch_size))
            self._send_message_batch(message_batch)

        return True

    def _send_message_batch(self, message_batch):
        try:
            result = self._connection.put_records(records = message_batch, stream_name=self._stream_name)
            if result.get('FailedRecordCount', 0) > 0:
                self._logger.error('Error occurred sending records to Kinesis stream {0}. result: {1}'.format(
                    self._stream_name, result))
                raise TransportException('Error occurred sending records to stream {0}'.format(self._stream_name))
        except Exception, e:
            self._logger.exception('Exception occurred sending records to Kinesis stream')
            raise TransportException(e.message)

    def interrupt(self):
        return True

    def unhandled(self):
        return True
