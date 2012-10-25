import datetime

import beaver.transport


class StdoutTransport(beaver.transport.Transport):

    def callback(self, filename, lines):
        timestamp = datetime.datetime.utcnow().isoformat()

        for line in lines:
            print self.format(filename, timestamp, line)
