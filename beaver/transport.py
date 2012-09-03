import os
import socket

BEAVER_FORMAT = os.environ.get('BEAVER_FORMAT', 'json')

if BEAVER_FORMAT == 'json':
    # priority: ujson > simplejson > jsonlib2 > json
    priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
    for mod in priority:
        try:
            json = __import__(mod)
        except ImportError:
            pass
        else:
            break
elif BEAVER_FORMAT == 'msgpack':
    import msgpack
else:
    BEAVER_FORMAT = None


class Transport(object):

    def __init__(self, configfile):
        self.current_host = socket.gethostname()
        self.configfile = configfile
        if BEAVER_FORMAT == 'msgpack':
            self.packer = msgpack.Packer()

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
                '@type': self.configfile.gettype(filename),
                '@tags': self.configfile.gettags(filename),
                '@fields': self.configfile.getaddfield(filename),
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
        elif BEAVER_FORMAT == 'msgpack':
            return self.packer.pack({
                '@source': "file://{0}{1}".format(self.current_host, filename),
                '@type': self.configfile.gettype(filename),
                '@tags': self.configfile.gettags(filename),
                '@fields': self.configfile.getaddfield(filename),
                '@timestamp': timestamp,
                '@source_host': self.current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })

        return "[{0}] [{1}] {2}".format(self.current_host, timestamp, line)
