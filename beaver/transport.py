import os


def create_transport(beaver_config, file_config):
    """Creates and returns a transport object"""
    if beaver_config.get('transport') == 'rabbitmq':
        import beaver.rabbitmq_transport
        transport = beaver.rabbitmq_transport.RabbitmqTransport(beaver_config, file_config)
    elif beaver_config.get('transport') == 'redis':
        import beaver.redis_transport
        transport = beaver.redis_transport.RedisTransport(beaver_config, file_config)
    elif beaver_config.get('transport') == 'stdout':
        import beaver.stdout_transport
        transport = beaver.stdout_transport.StdoutTransport(beaver_config, file_config)
    elif beaver_config.get('transport') == 'udp':
        import beaver.udp_transport
        transport = beaver.udp_transport.UdpTransport(beaver_config, file_config)
    elif beaver_config.get('transport') == 'zmq':
        import beaver.zmq_transport
        transport = beaver.zmq_transport.ZmqTransport(beaver_config, file_config)
    else:
        raise Exception('Invalid transport {0}'.format(beaver_config.get('transport')))

    return transport


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
