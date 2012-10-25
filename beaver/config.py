import ConfigParser
import glob
import logging
import os

import utils


class Config():
    '''
    Parse a given INI-style config file using ConfigParser module.
    Stanza's names match file names, and properties are defaulted as in
    http://logstash.net/docs/1.1.1/inputs/file

    Config file example:

    [/var/log/syslog]
    type: syslog
    tags: sys,main

    [/var/log/auth]
    type: syslog
    ;tags: auth,main

    [...]
    '''

    def __init__(self, configfile):
        logger = logging.getLogger('beaver')
        logger.info('Processing config file %s' % configfile)

        defaults = {
            'add_field': '',
            'debug': '',
            'discover_interval': '15',
            'exclude': '',
            'format': '',
            'message_format': '',
            'sincedb_path': '',
            'sincedb_write_interval': '15',
            'stat_interval': '1',
            'tags': '',
            'type': ''
        }
        self._configfile = configfile
        self._config = ConfigParser.ConfigParser(defaults)
        self._sanitize()
        self._data = self._parse()

    def _sanitize(self):
        if len(self._config.read(self._configfile)) != 1:
            raise Exception('Could not parse config file "%s"'
                % self._configfile)

    def _parse(self):
        inputs = {}
        for filename in self._config.sections():
            if not self._config.get(filename, 'type'):
                raise Exception('%s: missing mandatory config "type"'
                    % filename
                )
            globs = glob.glob(filename)
            if not globs:
                raise Exception('%s is not a valid file path' % filename)
            else:
                for globbed in glob.glob(filename):
                    configs = {x[0]: x[1] for x in self._config.items(filename)}
                    inputs[os.path.realpath(globbed)] = configs
        return inputs

    def _getfield(self, filename, field):
        return self._data.get(os.path.realpath(filename))[field]

    def getfilepaths(self):
        return self._data.keys()

    def gettype(self, filename):
        try:
            result = self._getfield(filename, 'type')
            return result if result else "file"
        except TypeError:
            return "file"

    def gettags(self, filename):
        try:
            result = self._getfield(filename, 'tags').split(",")
            return result if result else []
        except TypeError, err:
            return []

    def getaddfield(self, filename):
        try:
            result = self._getfield(filename, 'add_field').split(",")
            if result == ['']:
                return {}
            if (len(result) % 2) == 1:
                raise Exception('Wrong number of values for add_field')
            fieldkeys = result[0::2]
            fieldvalues = [[x] for x in result[1::2]]
            return dict(zip(fieldkeys, fieldvalues))
        except TypeError, err:
            return {}

    #  TODO: add support for any file property
