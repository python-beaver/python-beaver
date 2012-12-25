import datetime

import beaver.transport


class StdoutTransport(beaver.transport.Transport):

    def __init__(self, beaver_config, file_config, logger=None):
        super(StdoutTransport, self).__init__(beaver_config, file_config, logger=logger)
    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        for line in lines:
            print self.format(filename, timestamp, line)
