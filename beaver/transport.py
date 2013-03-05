import os


def create_transport(beaver_config, file_config, logger):
    """Creates and returns a transport object"""
    transport_str = beaver_config.get('transport')
    if '.' not in transport_str:
        # allow simple names like 'redis' to load a beaver built-in transport
        module_path = 'beaver.%s_transport' % transport_str.lower()
        class_name = '%sTransport' % transport_str.title()
    else:
        # allow dotted path names to load a custom transport class
        try:
            module_path, class_name = transport_str.rsplit('.', 1)
        except ValueError:
            raise Exception('Invalid transport {0}'.format(beaver_config.get('transport')))

    _module = __import__(module_path, globals(), locals(), class_name, -1)
    transport_class = getattr(_module, class_name)
    transport = transport_class(beaver_config, file_config, logger)

    return transport


class Transport(object):

    def __init__(self, beaver_config, file_config, logger=None):
        """Generic transport configuration
        Will attach the file_config object, setup the
        current hostname, and ensure we have a proper
        formatter for the current transport
        """
        self._current_host = beaver_config.get('hostname')
        self._file_config = file_config
        self._is_valid = True

        if beaver_config.get('format') == 'msgpack':
            import msgpack
            packer = msgpack.Packer()
            self._formatter = packer.pack
        elif beaver_config.get('format') == 'json':
            # priority: ujson > simplejson > jsonlib2 > json
            priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
            for mod in priority:
                try:
                    json = __import__(mod)
                    self._formatter = json.dumps
                except ImportError:
                    pass
                else:
                    break
        elif beaver_config.get('format') == 'string':
            def string_formatter(data):
                return "[{0}] [{1}] {2}".format(data['@source_host'], data['@timestamp'], data['@message'])
            self._formatter = string_formatter
        else:
            def null_formatter(data):
                return data['@message']
            self._formatter = null_formatter

    def callback(self, filename, lines):
        """Processes a set of lines for a filename"""
        return True

    def reconnect(self):
        """Allows reconnection from when a handled
        TransportException is thrown"""
        return True

    def interrupt(self):
        """Allows keyboard interrupts to be
        handled properly by the transport
        """
        return True

    def unhandled(self):
        """Allows unhandled exceptions to be
        handled properly by the transport
        """
        return True

    def format(self, filename, timestamp, line):
        """Returns a formatted log line"""
        return self._formatter({
            '@source': "file://{0}{1}".format(self._current_host, filename),
            '@type': self._file_config.get('type', filename),
            '@tags': self._file_config.get('tags', filename),
            '@fields': self._file_config.get('fields', filename),
            '@timestamp': timestamp,
            '@source_host': self._current_host,
            '@source_path': filename,
            '@message': line.strip(os.linesep),
        })

    def addglob(self, globname, globbed):
        self._file_config.addglob(globname, globbed)

    def valid(self):
        return self._is_valid


class TransportException(Exception):
    pass
