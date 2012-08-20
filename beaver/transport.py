import os
import socket

# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break

BEAVER_FORMAT = os.environ.get('BEAVER_FORMAT', 'json')


class Transport(object):

    def __init__(self):
        self.current_host = socket.gethostname()

    def callback(self, filename, lines):
        return True

    def interrupt(self):
        return True

    def unhandled(self):
        return True

    def format(self, filename, timestamp, line):
        if BEAVER_FORMAT == 'json':
            return json.dumps({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': "file",
                '@tags': [],
                '@fields': {},
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })

        return "[{0}] [{1}] {2}".format(self.current_host, timestamp, line)
