import ConfigParser
import collections
import os
import socket
import warnings


class BeaverConfig():

    def __init__(self, args, logger):
        self._logger = logger
        self._logger.info('Processing beaver portion of config file %s' % args.config)

        # Support env variable parsing as well
        files = os.environ.get("BEAVER_FILES", None)
        if files is not None:
            files = files.split(',')

        self._beaver_defaults = {
            'rabbitmq_host': os.environ.get('RABBITMQ_HOST', 'localhost'),
            'rabbitmq_port': os.environ.get('RABBITMQ_', '5672'),
            'rabbitmq_vhost': os.environ.get('RABBITMQ_', '/'),
            'rabbitmq_username': os.environ.get('RABBITMQ_', 'guest'),
            'rabbitmq_password': os.environ.get('RABBITMQ_', 'guest'),
            'rabbitmq_queue': os.environ.get('RABBITMQ_', 'logstash-queue'),
            'rabbitmq_exchange': os.environ.get('RABBITMQ_', 'direct'),
            'rabbitmq_exchange_durable': os.environ.get('RABBITMQ_EXCHANGE_DURABLE', '0'),
            'rabbitmq_key': os.environ.get('RABBITMQ_', 'logstash-key'),
            'rabbitmq_exchange': os.environ.get('RABBITMQ_', 'logstash-exchange'),
            'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'redis_namespace': os.environ.get('REDIS_NAMESPACE', 'logstash:beaver'),
            'udp_host': os.environ.get('UDP_HOST', '127.0.0.1'),
            'udp_port': os.environ.get('UDP_PORT', '9999'),
            'zeromq_address': os.environ.get('ZEROMQ_ADDRESS', 'tcp://localhost:2120'),
            'format': os.environ.get('BEAVER_FORMAT', 'json'),

            # exponential backoff
            'respawn_delay': '3',
            'max_failure': '7',

            # ssh tunnel support
            'ssh_key_file': None,
            'ssh_tunnel': None,
            'ssh_tunnel_port': None,
            'ssh_remote_host': None,
            'ssh_remote_port': None,

            # the following can be passed via argparse
            'zeromq_bind': os.environ.get('BEAVER_MODE', 'bind' if os.environ.get('BIND', False) else 'connect'),
            'files': files,
            'path': os.environ.get('BEAVER_PATH', '/var/log'),
            'transport': os.environ.get('BEAVER_TRANSPORT', 'stdout'),  # this needs to be passed to the import class somehow
            'fqdn': False,
            'hostname': None,
        }

        self._configfile = args.config
        self._beaver_config = self._parse_beaver_config(args)
        for key in self._beaver_config:
            self._logger.debug("[CONFIG] '{0}' => '{1}'".format(key, self._beaver_config.get(key)))

    def _parse_beaver_config(self, args):
        """Parses the configuration file for beaver configuration info

        Configuration priority:
            argparse > configfile > env var
        """
        _beaver_config = ConfigParser.ConfigParser(self._beaver_defaults)
        if len(_beaver_config.read(self._configfile)) != 1:
            raise Exception('Could not parse config file "%s"' % self._configfile)

        if not _beaver_config.has_section('beaver'):
            self._logger.debug('[CONFIG] Using beaver defaults')
            config = self._beaver_defaults
        else:
            self._logger.debug('[CONFIG] Reading beaver config from file')
            config = dict((x[0], x[1]) for x in _beaver_config.items('beaver'))

        if args.files:
            config['files'] = args.files
        if args.format:
            config['format'] = args.format
        if args.fqdn:
            config['fqdn'] = args.fqdn
        if args.mode:
            config['zeromq_bind'] = args.mode
        if args.path:
            config['path'] = args.path
        if args.transport:
            config['transport'] = args.transport

        if args.hostname:
            config['hostname'] = args.hostname

        if config.get('hostname') is None:
            if bool(config.get('fqdn')) == True:
                config['hostname'] = socket.getfqdn()
            else:
                config['hostname'] = socket.gethostname()

        config = collections.OrderedDict(sorted(config.items()))
        return config

    def get(self, key, default=None):
        return self._beaver_config.get(key, default)

    def set(self, key, value):
        self._beaver_config[key] = value

    def beaver_config(self):
        return self._beaver_config

    def update_files(self, config):
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

    def check_for_deprecated_usage(self):
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

