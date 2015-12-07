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
        self._epoch = datetime.datetime.utcfromtimestamp(0)

        self._logstash_version = beaver_config.get('logstash_version')
        if self._logstash_version == 0:
            self._fields = {
                'type': '@type',
                'tags': '@tags',
                'message': '@message',
                'file': '@source_path',
                'host': '@source_host',
                'raw_json_fields': ['@message', '@source', '@source_host', '@source_path', '@tags', '@timestamp', '@type'],
            }
        elif self._logstash_version == 1:
            self._fields = {
                'type': 'type',
                'tags': 'tags',
                'message': 'message',
                'file': 'file',
                'host': 'host',
                'raw_json_fields': ['message', 'host', 'file', 'tags', '@timestamp', 'type'],
            }

        def raw_formatter(data):
            return data[self._fields.get('message')]

        def rawjson_formatter(data):
            try:
                json_data = json.loads(data[self._fields.get('message')])
            except ValueError:
                self._logger.warning("cannot parse as rawjson: {0}".format(self._fields.get('message')))
                json_data = json.loads("{}")

            del data[self._fields.get('message')]

            for field in json_data:
                data[field] = json_data[field]

            for field in self._fields.get('raw_json_fields'):
                if field not in data:
                    data[field] = ''

            return json.dumps(data)

        def gelf_formatter(data):
            message = data[self._fields.get('message')]
            short_message = message.split('\n', 1)[0]
            short_message = short_message[:250]

            timestampDate = datetime.datetime.strptime(data['@timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

            delta = timestampDate - self._epoch
            timestampSeconds = delta.days*86400+delta.seconds+delta.microseconds/1e6

            gelf_data = {
                'version': '1.1',
                'host': data[self._fields.get('host')],
                'short_message': short_message,
                'full_message': message,
                'timestamp': timestampSeconds,
                'level': 6,
                '_file': data[self._fields.get('file')],
            }

            return json.dumps(gelf_data) + '\0'

        def string_formatter(data):
            return '[{0}] [{1}] {2}'.format(data[self._fields.get('host')], data['@timestamp'], data[self._fields.get('message')])

        self._formatters['json'] = json.dumps
        self._formatters['msgpack'] = msgpack.packb
        self._formatters['raw'] = raw_formatter
        self._formatters['rawjson'] = rawjson_formatter
        self._formatters['string'] = string_formatter
        self._formatters['gelf'] = gelf_formatter

    def addglob(self, globname, globbed):
        """Adds a set of globbed files to the attached beaver_config"""
        self._beaver_config.addglob(globname, globbed)

    def callback(self, filename, lines):
        """Processes a set of lines for a filename"""
        return True

    def format(self, filename, line, timestamp, **kwargs):
        """Returns a formatted log line"""
        line = unicode(line.encode("utf-8")[:32766], "utf-8", errors="ignore")
        formatter = self._beaver_config.get_field('format', filename)
        if formatter not in self._formatters:
            formatter = self._default_formatter

        data = {
            self._fields.get('type'): kwargs.get('type'),
            self._fields.get('tags'): kwargs.get('tags'),
            '@timestamp': timestamp,
            self._fields.get('host'): self._current_host,
            self._fields.get('file'): filename,
            self._fields.get('message'): line
        }

        if self._logstash_version == 0:
            data['@source'] = 'file://{0}'.format(filename)
            data['@fields'] = kwargs.get('fields')
        else:
            data['@version'] = self._logstash_version
            fields = kwargs.get('fields')
            for key in fields:
                data[key] = fields.get(key)

        return self._formatters[formatter](data)

    def get_timestamp(self, **kwargs):
        """Retrieves the timestamp for a given set of data"""
        timestamp = kwargs.get('timestamp')
        if not timestamp:
            now = datetime.datetime.utcnow()
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z"

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
