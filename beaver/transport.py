from beaver.event import Event


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
        """Generic transport configuration
        Will attach the file_config object, setup the
        current hostname, and ensure we have a proper
        formatter for the current transport
        """
        self._file_config = file_config
        self._current_host = beaver_config.get('hostname')

        if beaver_config.get('format') in ['json', 'msgpack']:
            if beaver_config.get('format') == 'msgpack':
                import msgpack
                packer = msgpack.Packer()

                def msgpack_formatter(event):
                    return packer.pack(event.to_dict())

                self._formatter = msgpack_formatter
            elif beaver_config.get('format') == 'json':
                # priority: ujson > simplejson > jsonlib2 > json
                priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
                json = None
                for mod in priority:
                    try:
                        json = __import__(mod)
                    except ImportError:
                        json = None
                        pass
                    else:
                        break

                def json_formatter(event):
                    return json.dumps(event.to_dict())

                self._formatter = json_formatter

        elif beaver_config.get('format') == 'string':
            def string_formatter(event):
                return event

            self._formatter = string_formatter
        else:
            def null_formatter(event):
                return event.get('@message')

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
        return self._formatter(Event(filename, timestamp, line, self._current_host, self._file_config))


class TransportException(Exception):
    pass
