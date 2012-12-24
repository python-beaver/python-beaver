import os


class Transport(object):

    def __init__(self, beaver_config, file_config):
        self._file_config = file_config
        self._format = beaver_config.get('format')

        self._current_host = beaver_config.get('hostname')

        if self._format == 'msgpack':
            import msgpack
            self.packer = msgpack.Packer()
        elif self._format == 'json':
            # priority: ujson > simplejson > jsonlib2 > json
            priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
            for mod in priority:
                try:
                    self.json = __import__(mod)
                except ImportError:
                    pass
                else:
                    break

    def callback(self, filename, lines):
        return True

    def interrupt(self):
        return True

    def unhandled(self):
        return True

    def format(self, filename, timestamp, line):
        if self._format == 'json':
            return self.json.dumps({
                '@source': "file://{0}{1}".format(self._current_host, filename),
                '@type': self._file_config.get('type', filename),
                '@tags': self._file_config.get('tags', filename),
                '@fields': self._file_config.get('fields', filename),
                '@timestamp': timestamp,
                '@source_host': self._current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })
        elif self._format == 'msgpack':
            return self.packer.pack({
                '@source': "file://{0}{1}".format(self._current_host, filename),
                '@type': self._file_config.get('type', filename),
                '@tags': self._file_config.get('tags', filename),
                '@fields': self._file_config.get('fields', filename),
                '@timestamp': timestamp,
                '@source_host': self._current_host,
                '@source_path': filename,
                '@message': line.strip(os.linesep),
            })

        return "[{0}] [{1}] {2}".format(self._current_host, timestamp, line)


class TransportException(Exception):
    pass
