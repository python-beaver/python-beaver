import ConfigParser
import os

from utils import eglob


class FileConfig():
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

    def __init__(self, args, logger):
        self._logger = logger
        self._logger.info('Processing file portion of config file %s' % args.config)

        self._defaults = {
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

        self._configfile = args.config
        self._config = ConfigParser.ConfigParser(self._defaults)
        self._sanitize()
        self._files, self._globs = self._parse()
        self._default_config = self._gen_config(self._defaults)
        self._globbed = []

    def get(self, field, filename):
        self._logger.debug("Retrieving {0} for {1}".format(field, filename))
        return self._files.get(os.path.realpath(filename), self._default_config)[field]

    def addglob(self, globname, globbed):
        if globname not in self._globbed:
            self._logger.debug("Adding glob {0}".format(globname))
            config = self._globs.get(globname, self._defaults)
            config = self._gen_config(config)
            self._globs[globname] = config
            for key in config:
                self._logger.debug("Config: {0} => {1}".format(key, config[key]))
        else:
            config = self._globs.get(globname)

        for filename in globbed:
            self._files[filename] = config
        self._globbed.append(globname)

    def getfilepaths(self):
        return self._files.keys()

    def getglobs(self):
        return self._globs.keys()

    def _gen_config(self, config):
        fields = config.get('add_field', '')
        if type(fields) != dict:
            try:
                if type(fields) == str:
                    fields = filter(None, fields.split(','))
                if len(fields) == 0:
                    config['fields'] = {}
                elif (len(fields) % 2) == 1:
                    raise Exception('Wrong number of values for add_field')
                else:
                    fieldkeys = fields[0::2]
                    fieldvalues = [[x] for x in fields[1::2]]
                    config['fields'] = dict(zip(fieldkeys, fieldvalues))
            except TypeError:
                config['fields'] = {}

        if 'add_field' in config:
            del config['add_field']

        try:
            tags = config.get('tags', '')
            if type(tags) == str:
                tags = filter(None, tags.split(','))
            if len(tags) == 0:
                tags = []
            config['tags'] = tags
        except TypeError:
            config['tags'] = []

        try:
            file_type = config.get('type', 'file')
            if not file_type:
                file_type = 'file'
            config['type'] = file_type
        except:
            config['type'] = "file"

        return config

    def _parse(self):
        glob_paths = {}
        files = {}
        for filename in self._config.sections():
            if not self._config.get(filename, 'type'):
                raise Exception('%s: missing mandatory config "type"' % filename)

            config = dict((x[0], x[1]) for x in self._config.items(filename))
            glob_paths[filename] = config

            globs = eglob(filename)
            if not globs:
                self._logger.info('Skipping glob due to no files found: %s' % filename)
                continue

            for globbed_file in globs:
                files[os.path.realpath(globbed_file)] = config

        return files, glob_paths

    def _sanitize(self):
        if len(self._config.read(self._configfile)) != 1:
            raise Exception('Could not parse config file "%s"' % self._configfile)

        if self._config.has_section('beaver'):
            self._config.remove_section('beaver')
