import datetime

import beaver.transport


class StdoutTransport(beaver.transport.Transport):

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        for line in lines:
            print self.format(filename, timestamp, line)
