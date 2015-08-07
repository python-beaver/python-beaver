# -*- coding: utf-8 -*-
import boto.sns
import uuid

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException

class SnsTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(SnsTransport, self).__init__(beaver_config, logger=logger)

        self._access_key = beaver_config.get('sns_aws_access_key')
        self._secret_key = beaver_config.get('sns_aws_secret_key')
        self._profile = beaver_config.get('sns_aws_profile_name')
        self._region = beaver_config.get('sns_aws_region')
        self._topic_arn = beaver_config.get('sns_topic_arn')

        try:
            if self._profile:
                self._connection = boto.sns.connect_to_region(self._region,
                                                              profile_name=self._profile)
            elif self._access_key is None and self._secret_key is None:
                self._connection = boto.sns.connect_to_region(self._region)
            else:
                self._connection = boto.sns.connect_to_region(self._region,
                                                              aws_access_key_id=self._access_key,
                                                              aws_secret_access_key=self._secret_key)

            if self._connection is None:
                self._logger.warn('Unable to connect to AWS - check your AWS credentials')
                raise TransportException('Unable to connect to AWS - check your AWS credentials')

        except Exception, e:
            raise TransportException(e.message)

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            try:
                self._connection.publish(self._topic_arn, self.format(filename, line, timestamp, **kwargs))
            except Exception, e:
                self._logger.exception('Exception occurred sending to SNS topic')
                raise TransportException(e.message)

        return True

    def interrupt(self):
        return True

    def unhandled(self):
        return True
