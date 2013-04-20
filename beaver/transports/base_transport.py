# -*- coding: utf-8 -*-
import datetime

# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break

try:
    import msgpack
except ImportError:
    import msgpack_pure as msgpack


class BaseTransport(object):

    def __init__(self, beaver_config, logger=None):
        """Generic transport configuration
        Will attach the file_config object, setup the
        current hostname, and ensure we have a proper
        formatter for the current transport
        """
        self._beaver_config = beaver_config
        self._current_host = beaver_config.get('hostname')
        self._default_formatter = beaver_config.get('format', 'null')
        self._formatters = {}
        self._is_valid = True
        self._logger = logger

        def null_formatter(data):
            return data['@message']

        def rawjson_formatter(data):
            json_data = json.loads(data['@message'])
            del data['@message']

            for field in json_data:
                data[field] = json_data[field]

            for field in ['@message', '@source', '@source_host', '@source_path', '@tags', '@timestamp', '@type']:
                if field not in data:
                    data[field] = ''

            return json.dumps(data)

        def string_formatter(data):
            return '[{0}] [{1}] {2}'.format(data['@source_host'], data['@timestamp'], data['@message'])

        self._formatters['json'] = json.dumps
        self._formatters['msgpack'] = msgpack.packb
        self._formatters['null'] = null_formatter
        self._formatters['rawjson'] = rawjson_formatter
        self._formatters['string'] = string_formatter

    def addglob(self, globname, globbed):
        """Adds a set of globbed files to the attached beaver_config"""
        self._beaver_config.addglob(globname, globbed)

    def callback(self, filename, lines):
        """Processes a set of lines for a filename"""
        return True

    def format(self, filename, line, timestamp, **kwargs):
        """Returns a formatted log line"""
        formatter = self._beaver_config.get_field('format', filename)
        if formatter not in self._formatters:
            formatter = self._default_formatter

        return self._formatters[formatter]({
            '@source': 'file://{0}{1}'.format(self._current_host, filename),
            '@type': kwargs.get('type'),
            '@tags': kwargs.get('tags'),
            '@fields': kwargs.get('fields'),
            '@timestamp': timestamp,
            '@source_host': self._current_host,
            '@source_path': filename,
            '@message': line,
        })

    def get_timestamp(self, **kwargs):
        """Retrieves the timestamp for a given set of data"""
        timestamp = kwargs.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.utcnow().isoformat() + 'Z'

        return timestamp

    def interrupt(self):
        """Allows keyboard interrupts to be
        handled properly by the transport
        """
        return True

    def invalidate(self):
        """Invalidates the current transport"""
        self._is_valid = False

    def reconnect(self):
        """Allows reconnection from when a handled
        TransportException is thrown"""
        return True

    def unhandled(self):
        """Allows unhandled exceptions to be
        handled properly by the transport
        """
        return True

    def valid(self):
        """Returns whether or not the transport can send data"""
        return self._is_valid
