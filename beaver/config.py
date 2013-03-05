import ConfigParser
import logging
import os
import socket
import warnings

from beaver.utils import eglob


class BeaverConfig():

    def __init__(self, args, file_config=None, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        self._logger.debug('Processing beaver portion of config file %s' % args.config)

        self._beaver_defaults = {
            'rabbitmq_host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'rabbitmq_port': os.environ.get('RABBITMQ_PORT', '5672'),
            'rabbitmq_vhost': os.environ.get('RABBITMQ_VHOST', '/'),
            'rabbitmq_username': os.environ.get('RABBITMQ_USERNAME', 'guest'),
            'rabbitmq_password': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
            'rabbitmq_queue': os.environ.get('RABBITMQ_QUEUE', 'logstash-queue'),
            'rabbitmq_exchange_type': os.environ.get('RABBITMQ_EXCHANGE_TYPE', 'direct'),
            'rabbitmq_exchange_durable': os.environ.get('RABBITMQ_EXCHANGE_DURABLE', '0'),
            'rabbitmq_key': os.environ.get('RABBITMQ_KEY', 'logstash-key'),
            'rabbitmq_exchange': os.environ.get('RABBITMQ_EXCHANGE', 'logstash-exchange'),
            'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'redis_namespace': os.environ.get('REDIS_NAMESPACE', 'logstash:beaver'),
            'redis_password': '',
            'udp_host': os.environ.get('UDP_HOST', '127.0.0.1'),
            'udp_port': os.environ.get('UDP_PORT', '9999'),
            'zeromq_address': os.environ.get('ZEROMQ_ADDRESS', 'tcp://localhost:2120'),
            'zeromq_hwm': os.environ.get('ZEROMQ_HWM', ''),

            # exponential backoff
            'respawn_delay': '3',
            'max_failure': '7',

            # interprocess queue max size before puts block
            'max_queue_size': '100',

            # time in seconds before updating the file mapping
            'update_file_mapping_time': '10',

            # time in seconds from last command sent before a queue kills itself
            'queue_timeout': '60',

            # time in seconds to wait on queue.get() block before raising Queue.Empty exception
            'wait_timeout': '5',

            # ssh tunnel support
            'ssh_key_file': '',
            'ssh_tunnel': '',
            'ssh_tunnel_port': '',
            'ssh_remote_host': '',
            'ssh_remote_port': '',
            'subprocess_poll_sleep': '1',

            # the following can be passed via argparse
            'zeromq_bind': os.environ.get('BEAVER_MODE', 'bind' if os.environ.get('BIND', False) else 'connect'),
            'files': os.environ.get('BEAVER_FILES', ''),
            'format': os.environ.get('BEAVER_FORMAT', 'json'),
            'fqdn': '0',
            'hostname': '',
            'output': '',
            'path': os.environ.get('BEAVER_PATH', '/var/log'),
            'transport': os.environ.get('BEAVER_TRANSPORT', 'stdout'),  # this needs to be passed to the import class somehow

            # the following are parsed before the config file is parsed
            # but may be useful at runtime
            'config': '/dev/null',
            'debug': '0',
            'daemonize': '0',
            'pid': '',
        }

        self._configfile = args.config
        self._beaver_config = self._parse(args)
        for key in self._beaver_config:
            self._logger.debug("[CONFIG] '{0}' => '{1}'".format(key, self._beaver_config.get(key)))

        if file_config is not None:
            self._update_files(file_config)

        self._check_for_deprecated_usage()

    def beaver_config(self):
        return self._beaver_config

    def get(self, key, default=None):
        return self._beaver_config.get(key, default)

    def set(self, key, value):
        self._beaver_config[key] = value

    def use_ssh_tunnel(self):
        required = [
            'ssh_key_file',
            'ssh_tunnel',
            'ssh_tunnel_port',
            'ssh_remote_host',
            'ssh_remote_port',
        ]

        has = len(filter(lambda x: self.get(x) != None, required))
        if has > 0 and has != len(required):
            self._logger.warning("Missing {0} of {1} required config variables for ssh".format(len(required) - has, len(required)))

        return has == len(required)

    def _check_for_deprecated_usage(self):
        env_vars = [
          'RABBITMQ_HOST',
          'RABBITMQ_PORT',
          'RABBITMQ_VHOST',
          'RABBITMQ_USERNAME',
          'RABBITMQ_PASSWORD',
          'RABBITMQ_QUEUE',
          'RABBITMQ_EXCHANGE_TYPE',
          'RABBITMQ_EXCHANGE_DURABLE',
          'RABBITMQ_KEY',
          'RABBITMQ_EXCHANGE',
          'REDIS_URL',
          'REDIS_NAMESPACE',
          'UDP_HOST',
          'UDP_PORT',
          'ZEROMQ_ADDRESS',
          'BEAVER_FILES',
          'BEAVER_FORMAT',
          'BEAVER_MODE',
          'BEAVER_PATH',
          'BEAVER_TRANSPORT',
        ]

        deprecated_env_var_usage = []

        for e in env_vars:
            v = os.environ.get(e, None)
            if v is not None:
                deprecated_env_var_usage.append(e)

        if len(deprecated_env_var_usage) > 0:
            warnings.simplefilter('default')
            warnings.warn('ENV Variable support will be removed by version 20. Stop using: {0}'.format(", ".join(deprecated_env_var_usage)), DeprecationWarning)

    def _parse(self, args):
        """Parses the configuration file for beaver configuration info

        Configuration priority:
            argparse > configfile > env var
        """
        _beaver_config = ConfigParser.ConfigParser(self._beaver_defaults)
        if self._configfile and len(_beaver_config.read(self._configfile)) != 1:
            raise Exception('Could not parse config file "%s"' % self._configfile)

        if not _beaver_config.has_section('beaver'):
            self._logger.debug('[CONFIG] Using beaver defaults')
            config = self._beaver_defaults
        else:
            self._logger.debug('[CONFIG] Reading beaver config from file')
            config = dict((x[0], x[1]) for x in _beaver_config.items('beaver'))

        transpose = ['config', 'debug', 'daemonize', 'files', 'format', 'fqdn', 'hostname', 'path', 'pid', 'transport']
        namspace_dict = vars(args)
        for key in transpose:
            if key not in namspace_dict:
                continue
            if namspace_dict[key] is None:
                continue
            if namspace_dict[key] == '':
                continue
            config[key] = namspace_dict[key]

        if args.mode:
            config['zeromq_bind'] = args.mode

        # HACK: Python 2.6 ConfigParser does not properly
        #       handle non-string values
        for key in config:
            if config[key] == '':
                config[key] = None

        require_bool = ['debug', 'daemonize', 'fqdn', 'rabbitmq_exchange_durable']

        for key in require_bool:
            config[key] = bool(config[key])

        require_int = [
            'max_failure',
            'max_queue_size',
            'queue_timeout',
            'rabbitmq_port',
            'respawn_delay',
            'subprocess_poll_sleep',
            'udp_port',
            'wait_timeout',
            'zeromq_hwm',
        ]
        for key in require_int:
            if config[key] is not None:
                config[key] = int(config[key])

        require_float = [
            'update_file_mapping_time',
        ]

        for key in require_float:
            if config[key] is not None:
                config[key] = float(config[key])

        if config['files'] is not None and type(config['files']) == str:
            config['files'] = config['files'].split(',')

        config['path'] = os.path.realpath(config['path'])
        if not os.path.isdir(config['path']):
            raise LookupError('{0} does not exist'.format(config['path']))

        if config.get('hostname') is None:
            if config.get('fqdn') == True:
                config['hostname'] = socket.getfqdn()
            else:
                config['hostname'] = socket.gethostname()

        return config

    def _update_files(self, config):
        globs = self.get('files', default=[])
        files = self.get('files', default=[])

        try:
            files.extend(config.getfilepaths())
            globs.extend(config.getglobs())
        except AttributeError:
            files = config.getfilepaths()
            globs = config.getglobs()

        self.set('globs', globs)
        self.set('files', files)


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

    def __init__(self, args, logger=None):
        self._logger = logger
        self._logger.debug('Processing file portion of config file %s' % args.config)

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
                self._logger.debug('Skipping glob due to no files found: %s' % filename)
                continue

            for globbed_file in globs:
                files[os.path.realpath(globbed_file)] = config

        return files, glob_paths

    def _sanitize(self):
        if len(self._config.read(self._configfile)) != 1:
            raise Exception('Could not parse config file "%s"' % self._configfile)

        if self._config.has_section('beaver'):
            self._config.remove_section('beaver')
