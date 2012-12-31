import os


def create_transport(beaver_config, file_config, logger):
    """Creates and returns a transport object"""
    if beaver_config.get('transport') == 'rabbitmq':
        import beaver.rabbitmq_transport
        transport = beaver.rabbitmq_transport.RabbitmqTransport(beaver_config, file_config, logger)
    elif beaver_config.get('transport') == 'redis':
        import beaver.redis_transport
        transport = beaver.redis_transport.RedisTransport(beaver_config, file_config, logger)
    elif beaver_config.get('transport') == 'stdout':
        import beaver.stdout_transport
        transport = beaver.stdout_transport.StdoutTransport(beaver_config, file_config, logger)
    elif beaver_config.get('transport') == 'udp':
        import beaver.udp_transport
        transport = beaver.udp_transport.UdpTransport(beaver_config, file_config, logger)
    elif beaver_config.get('transport') == 'zmq':
        import beaver.zmq_transport
        transport = beaver.zmq_transport.ZmqTransport(beaver_config, file_config, logger)
    else:
        raise Exception('Invalid transport {0}'.format(beaver_config.get('transport')))

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
            def string_formatter(self, data):
                return "[{0}] [{1}] {2}".format(data['@source_host'], data['@timestamp'], data['@message'])
            self._formatter = string_formatter
        else:
            def null_formatter(self, data):
                return data['@message']
            self._formatter = null_formatter

    def callback(self, filename, lines):
        """Processes a set of lines for a filename"""
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


class TransportException(Exception):
    pass
