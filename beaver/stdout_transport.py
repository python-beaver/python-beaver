import datetime

import beaver.transport


class StdoutTransport(beaver.transport.Transport):

    def callback(self, filename, lines):
        timestamp = datetime.datetime.now().isoformat()

        for line in lines:
            print self.format(filename, timestamp, line, self.gettype(filename))
