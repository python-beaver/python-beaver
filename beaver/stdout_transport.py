import datetime

import beaver.transport
import beaver.utils


class StdoutTransport(beaver.transport.Transport):

    def __init__(self, beaver_config, file_config, logger=None):
        super(StdoutTransport, self).__init__(beaver_config, file_config, logger=logger)
        self._logger = beaver.utils.setup_custom_logger('stdout', formatter=False, output=beaver_config.get('output'))

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        for line in lines:
            self._logger.info(self.format(filename, timestamp, line))
