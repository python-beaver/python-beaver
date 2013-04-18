# -*- coding: utf-8 -*-
from beaver.transports.base_transport import BaseTransport
from beaver.utils import setup_custom_logger


class StdoutTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(StdoutTransport, self).__init__(beaver_config, logger=logger)
        self._stdout = setup_custom_logger('stdout', formatter=False, output=beaver_config.get('output'))

    def callback(self, filename, lines, **kwargs):
        timestamp = self.get_timestamp(**kwargs)
        if kwargs.get('timestamp', False):
            del kwargs['timestamp']

        for line in lines:
            self._stdout.info(self.format(filename, line, timestamp, **kwargs))
