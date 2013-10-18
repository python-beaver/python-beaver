# -*- coding: utf-8 -*-
import logging
import os
import re
import socket
import warnings

from conf_d import Configuration
from beaver.utils import eglob


class BeaverConfig():

    def __init__(self, args, logger=None):
        self._logger = logger or logging.getLogger(__name__)
        self._logger.debug('Processing beaver portion of config file %s' % args.config)

        self._section_defaults = {
            'add_field': '',
            'debug': '0',
            'discover_interval': '15',
            'encoding': 'utf_8',

            # should be a python regex of files to remove
            'exclude': '',
            'format': '',

            # throw out empty lines instead of shipping them
            'ignore_empty': '0',

            # allow ignoring copytruncate results
            'ignore_truncate': '0',

            # buffered tokenization
            # we string-escape the delimiter later so that we can put escaped characters in our config file
            'delimiter': '\n',
            'size_limit': '',

            # multiline events support. Default is disabled
            'multiline_regex_after': '',
            'multiline_regex_before': '',

            'message_format': '',
            'sincedb_write_interval': '15',
            'stat_interval': '1',
            'start_position': 'end',
            'tags': '',
            'tail_lines': '0',
            'type': '',
        }

        self._main_defaults = {
            'mqtt_clientid': 'mosquitto',
            'mqtt_host': 'localhost',
            'mqtt_port': '1883',
            'mqtt_topic': '/logstash',
            'mqtt_keepalive': '60',
            'rabbitmq_host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'rabbitmq_port': os.environ.get('RABBITMQ_PORT', '5672'),
            'rabbitmq_vhost': os.environ.get('RABBITMQ_VHOST', '/'),
            'rabbitmq_username': os.environ.get('RABBITMQ_USERNAME', 'guest'),
            'rabbitmq_password': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
            'rabbitmq_queue': os.environ.get('RABBITMQ_QUEUE', 'logstash-queue'),
            'rabbitmq_exchange_type': os.environ.get('RABBITMQ_EXCHANGE_TYPE', 'direct'),
            'rabbitmq_exchange_durable': os.environ.get('RABBITMQ_EXCHANGE_DURABLE', '0'),
            'rabbitmq_queue_durable': os.environ.get('RABBITMQ_QUEUE_DURABLE', '0'),
            'rabbitmq_ha_queue': os.environ.get('RABBITMQ_HA_QUEUE', '0'),
            'rabbitmq_key': os.environ.get('RABBITMQ_KEY', 'logstash-key'),
            'rabbitmq_exchange': os.environ.get('RABBITMQ_EXCHANGE', 'logstash-exchange'),
            'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'redis_namespace': os.environ.get('REDIS_NAMESPACE', 'logstash:beaver'),
            'redis_password': '',
            'sqs_aws_access_key': '',
            'sqs_aws_secret_key': '',
            'sqs_aws_region': 'us-east-1',
            'sqs_aws_queue': '',
            'tcp_host': '127.0.0.1',
            'tcp_port': '9999',
            'udp_host': os.environ.get('UDP_HOST', '127.0.0.1'),
            'udp_port': os.environ.get('UDP_PORT', '9999'),
            'zeromq_address': os.environ.get('ZEROMQ_ADDRESS', 'tcp://localhost:2120'),
            'zeromq_pattern': 'push',
            'zeromq_hwm': os.environ.get('ZEROMQ_HWM', ''),

            # exponential backoff
            'respawn_delay': '3',
            'max_failure': '7',

            # interprocess queue max size before puts block
            'max_queue_size': '100',

            # time in seconds before updating the file mapping
            'update_file_mapping_time': '',  # deprecated
            'discover_interval': '15',

            # time in seconds from last command sent before a queue kills itself
            'queue_timeout': '60',

            # kill and respawn worker process after given number of seconds
            'refresh_worker_process': '',

            # time in seconds to wait on queue.get() block before raising Queue.Empty exception
            'wait_timeout': '5',

            # path to sincedb sqlite db
            'sincedb_path': '',

            'logstash_version': '',

            # ssh tunnel support
            'ssh_key_file': '',
            'ssh_tunnel': '',
            'ssh_tunnel_port': '',
            'ssh_remote_host': '',
            'ssh_remote_port': '',
            'ssh_options': '',
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

            # Path to individual file configs. These override any sections in the main beaver.ini file
            'confd_path': '/etc/beaver/conf.d',

            # the following are parsed before the config file is parsed
            # but may be useful at runtime
            'config': '/dev/null',
            'debug': '0',
            'daemonize': '0',
            'pid': '',
        }

        self._configfile = args.config
        self._globbed = []
        self._parse(args)
        for key in self._beaver_config:
            self._logger.debug('[CONFIG] "{0}" => "{1}"'.format(key, self._beaver_config.get(key)))

        self._update_files()
        self._check_for_deprecated_usage()

    def beaver_config(self):
        return self._beaver_config

    def get(self, key, default=None):
        return self._beaver_config.get(key, default)

    def set(self, key, value):
        self._beaver_config[key] = value

    def get_field(self, field, filename):
        return self._files.get(os.path.realpath(filename), self._section_defaults)[field]

    def addglob(self, globname, globbed):
        if globname not in self._globbed:
            self._logger.debug('Adding glob {0}'.format(globname))
            config = self._file_config[globname]
            self._file_config[globname] = config
            for key in config:
                self._logger.debug('Config: "{0}" => "{1}"'.format(key, config[key]))
        else:
            config = self._file_config.get(globname)

        for filename in globbed:
            self._files[filename] = config
        self._globbed.append(globname)

    def getfilepaths(self):
        return self._files.keys()

    def getglobs(self):
        globs = []
        [globs.extend([name, self._file_config[name].get('exclude')]) for name in self._file_config]
        return dict(zip(globs[0::2], globs[1::2]))

    def use_ssh_tunnel(self):
        required = [
            'ssh_key_file',
            'ssh_tunnel',
            'ssh_tunnel_port',
            'ssh_remote_host',
            'ssh_remote_port',
        ]

        has = len(filter(lambda x: self.get(x) is not None, required))
        if has > 0 and has != len(required):
            self._logger.warning('Missing {0} of {1} required config variables for ssh'.format(len(required) - has, len(required)))

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
            warnings.warn('ENV Variable support will be removed by version 20. Stop using: {0}'.format(', '.join(deprecated_env_var_usage)), DeprecationWarning)

        update_file_mapping_time = self.get('update_file_mapping_time')
        if update_file_mapping_time:
            self.set('discover_interval', update_file_mapping_time)
            warnings.simplefilter('default')
            warnings.warn('"update_file_mapping_time" has been supersceded by "discover_interval". Stop using: "update_file_mapping_time', DeprecationWarning)

    def _parse(self, args):
        def _main_parser(config):
            transpose = ['config', 'confd_path', 'debug', 'daemonize', 'files', 'format', 'fqdn', 'hostname', 'path', 'pid', 'transport']
            namspace_dict = vars(args)
            for key in transpose:
                if key not in namspace_dict or namspace_dict[key] is None or namspace_dict[key] == '':
                    continue

                config[key] = namspace_dict[key]

            if args.mode:
                config['zeromq_bind'] = args.mode

            # HACK: Python 2.6 ConfigParser does not properly
            #       handle non-string values
            for key in config:
                if config[key] == '':
                    config[key] = None

            require_bool = ['debug', 'daemonize', 'fqdn', 'rabbitmq_exchange_durable', 'rabbitmq_queue_durable', 'rabbitmq_ha_queue']

            for key in require_bool:
                config[key] = bool(int(config[key]))

            require_int = [
                'max_failure',
                'max_queue_size',
                'queue_timeout',
                'rabbitmq_port',
                'respawn_delay',
                'subprocess_poll_sleep',
                'refresh_worker_process',
                'tcp_port',
                'udp_port',
                'wait_timeout',
                'zeromq_hwm',
                'logstash_version',
            ]
            for key in require_int:
                if config[key] is not None:
                    config[key] = int(config[key])

            require_float = [
                'update_file_mapping_time',
                'discover_interval',
            ]

            for key in require_float:
                if config[key] is not None:
                    config[key] = float(config[key])

            if config.get('format') == 'null':
                config['format'] = 'raw'

            if config['files'] is not None and type(config['files']) == str:
                config['files'] = config['files'].split(',')

            if config['path'] is not None:
                config['path'] = os.path.realpath(config['path'])
                if not os.path.isdir(config['path']):
                    raise LookupError('{0} does not exist'.format(config['path']))

            if config.get('hostname') is None:
                if config.get('fqdn') is True:
                    config['hostname'] = socket.getfqdn()
                else:
                    config['hostname'] = socket.gethostname()

            if config.get('sincedb_path'):
                config['sincedb_path'] = os.path.realpath(config.get('sincedb_path'))

            if config['zeromq_address'] and type(config['zeromq_address']) == str:
                config['zeromq_address'] = [x.strip() for x in config.get('zeromq_address').split(',')]

            if config.get('ssh_options') is not None:
                csv = config.get('ssh_options')
                config['ssh_options'] = []
                if csv == str:
                    for opt in csv.split(','):
                        config['ssh_options'].append('-o %s' % opt.strip())
            else:
                config['ssh_options'] = []

            config['globs'] = {}

            return config

        def _section_parser(config, raise_exceptions=True):
            '''Parse a given INI-style config file using ConfigParser module.
            Stanza's names match file names, and properties are defaulted as in
            http://logstash.net/docs/1.1.1/inputs/file

            Config file example:

            [/var/log/syslog]
            type: syslog
            tags: sys,main

            [/var/log/auth]
            type: syslog
            ;tags: auth,main
            '''

            fields = config.get('add_field', '')
            if type(fields) != dict:
                try:
                    if type(fields) == str:
                        fields = filter(None, fields.split(','))
                    if len(fields) == 0:
                        config['fields'] = {}
                    elif (len(fields) % 2) == 1:
                        if raise_exceptions:
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

            if config.get('format') == 'null':
                config['format'] = 'raw'

            file_type = config.get('type', None)
            if not file_type:
                config['type'] = 'file'

            require_bool = ['debug', 'ignore_empty', 'ignore_truncate']
            for k in require_bool:
                config[k] = bool(int(config[k]))

            config['delimiter'] = config['delimiter'].decode('string-escape')

            if config['multiline_regex_after']:
                config['multiline_regex_after'] = re.compile(config['multiline_regex_after'])
            if config['multiline_regex_before']:
                config['multiline_regex_before'] = re.compile(config['multiline_regex_before'])

            require_int = ['sincedb_write_interval', 'stat_interval', 'tail_lines']
            for k in require_int:
                config[k] = int(config[k])

            return config

        conf = Configuration(
            name='beaver',
            path=self._configfile,
            main_defaults=self._main_defaults,
            section_defaults=self._section_defaults,
            main_parser=_main_parser,
            section_parser=_section_parser,
            path_from_main='confd_path'
        )

        config = conf.raw()
        self._beaver_config = config['beaver']
        self._file_config = config['sections']

        self._main_parser = _main_parser(self._main_defaults)
        self._section_defaults = _section_parser(self._section_defaults, raise_exceptions=False)

        self._files = {}
        for section in config['sections']:
            globs = eglob(section, config['sections'][section].get('exclude', ''))
            if not globs:
                self._logger.debug('Skipping glob due to no files found: %s' % section)
                continue

            for globbed_file in globs:
                self._files[os.path.realpath(globbed_file)] = config['sections'][section]

    def _update_files(self):
        globs = self.get('files', default=[])
        files = self.get('files', default=[])

        if globs:
            globs = dict(zip(globs, [None]*len(globs)))
        else:
            globs = {}

        try:
            files.extend(self.getfilepaths())
            globs.update(self.getglobs())
        except AttributeError:
            files = self.getfilepaths()
            globs = self.getglobs()

        self.set('globs', globs)
        self.set('files', files)

        for f in files:
            if f not in self._file_config:
                self._file_config[f] = self._section_defaults
