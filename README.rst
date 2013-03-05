======
Beaver
======

python daemon that munches on logs and sends their contents to logstash

Requirements
============

* Python 2.6+
* Optional zeromq support: install libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``) and pyzmq (``pip install pyzmq==2.1.11``)

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/beaver.git#egg=beaver

From PyPI::

    pip install beaver==28

Usage
=====

usage::

    beaver [-h] [-c CONFIG] [-d] [-D] [-f FILES [FILES ...]]
            [-F {json,msgpack,string,raw}] [-H HOSTNAME] [-m {bind,connect}]
            [-l OUTPUT] [-p PATH] [-P PID]
            [-t {rabbitmq,redis,stdout,zmq,udp}] [-v] [--fqdn]

optional arguments::

    -h, --help            show this help message and exit
    -c CONFIG, --configfile CONFIG
                          ini config file path
    -d, --debug           enable debug mode
    -D, --daemonize       daemonize in the background
    -f FILES [FILES ...], --files FILES [FILES ...]
                          space-separated filelist to watch, can include globs
                          (*.log). Overrides --path argument
    -F {json,msgpack,string,raw}, --format {json,msgpack,string,raw}
                          format to use when sending to transport
    -H HOSTNAME, --hostname HOSTNAME
                          manual hostname override for source_host
    -m {bind,connect}, --mode {bind,connect}
                          bind or connect mode
    -l OUTPUT, --logfile OUTPUT, -o OUTPUT, --output OUTPUT
                          file to pipe output to (in addition to stdout)
    -p PATH, --path PATH  path to log files
    -P PID, --pid PID     path to pid file
    -t {rabbitmq,redis,stdout,zmq,udp}, --transport {rabbitmq,redis,stdout,zmq,udp}
                          log transport method
    -v, --version         output version and quit
    --fqdn                use the machine's FQDN for source_host

Background
==========

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using either redis, stdin, zeromq as the transport. This means you'll need a redis, stdin, zeromq input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

NOTE: the redis transport uses a namespace of ``logstash:beaver`` by default.  You will need to update your logstash indexer to match this, or you may configure beaver to do otherwise.

Configuration File Options
--------------------------

Beaver can optionally get data from a ``configfile`` using the ``-c`` flag. This file is in ``ini`` format. Global configuration will be under the ``beaver`` stanza. The following are global beaver configuration keys with their respective meanings:

* rabbitmq_host: Defaults ``localhost``. Host for RabbitMQ.
* rabbitmq_port: Defaults ``5672``. Port for RabbitMQ.
* rabbitmq_vhost: Default ``/``
* rabbitmq_username: Default ``guest``
* rabbitmq_password: Default ``guest``
* rabbitmq_queue: Default ``logstash-queue``.
* rabbitmq_exchange_type: Default ``direct``.
* rabbitmq_exchange_durable: Default ``0``.
* rabbitmq_key: Default ``logstash-key``.
* rabbitmq_exchange: Default ``logstash-exchange``.
* redis_url: Default ``redis://localhost:6379/0``. Redis URL
* redis_namespace: Default ``logstash:beaver``. Redis key namespace
* udp_host: Default ``127.0.0.1``. UDP Host
* udp_port: Default ``9999``. UDP Port
* zeromq_address: Default ``tcp://localhost:2120``. Zeromq URL
* zeromq_hwm: Default None. Zeromq HighWaterMark socket option
* zeromq_bind: Default ``bind``. Whether to bind to zeromq host or simply connect

The following are used for instances when a TransportException is thrown - Transport dependent

* respawn_delay: Default ``3``. Initial respawn delay for exponential backoff
* max_failure: Default ``7``. Max failures before exponential backoff terminates

The following configuration keys are for building an SSH Tunnel that can be used to proxy from the current host to a desired server. This proxy is torn down when Beaver halts in all cases.

* ssh_key_file: Default ``None``. Full path to ``id_rsa`` key file
* ssh_tunnel: Default ``None``. SSH Tunnel in the format ``user@host:port``
* ssh_tunnel_port: Default ``None``. Local port for SSH Tunnel
* ssh_remote_host: Default ``None``. Remote host to connect to within SSH Tunnel
* ssh_remote_port: Default ``None``. Remote port to connect to within SSH Tunnel

The following can also be passed via argparse. Argparse will override all options in the configfile, when specified.

* format: Default ``json``. Options ``[ json, msgpack, string ]``. Format to use when sending to transport
* files: Default ``files``. Space-separated list of files to tail. (Comma separated if specified in the config file)
* path: Default ``/var/log``. Path glob to tail.
* transport: Default ``stdout``. Transport to use when log changes are detected
* fqdn: Default ``False``. Whether to use the machine's FQDN in transport output
* hostname: Default ``None``. Manually specified hostname

Examples
--------


Example 1: Listen to all files in the default path of /var/log on standard out as json::

    beaver

Example 2: Listen to all files in the default path of /var/log on standard out with msgpack::

    beaver --format msgpack

Example 3: Listen to all files in the default path of /var/log on standard out as a string::

    beaver --format string

Example 4: Sending logs from /var/log files to a redis list::

    # /etc/beaver.conf
    [beaver]
    redis_url: redis://localhost:6379/0

    # From the commandline
    beaver  -c /etc/beaver.conf -t redis

Example 5: Use environment variables to send logs from /var/log files to a redis list::

    # /etc/beaver.conf
    [beaver]
    redis_url: redis://localhost:6379/0

    # From the commandline
    beaver  -c /etc/beaver.conf -p '/var/log' -t redis

Example 6: Zeromq listening on port 5556 (all interfaces)::

    # /etc/beaver.conf
    [beaver]
    zeromq_address: tcp://*:5556

    # logstash indexer config:
    input {
      zeromq {
        type => 'shipper-input'
        mode => 'client'
        topology => 'pushpull'
        address => 'tcp://shipperhost:5556'
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver  -c /etc/beaver.conf -m bind -t zmq


Example 7: Zeromq connecting to remote port 5556 on indexer::

    # /etc/beaver.conf
    [beaver]
    zeromq_address: tcp://indexer:5556

    # logstash indexer config:
    input {
      zeromq {
        type => 'shipper-input'
        mode => 'server'
        topology => 'pushpull'
        address => 'tcp://*:5556'
      }
    }
    output { stdout { debug => true } }

    # on the commandline
    beaver -c /etc/beaver.conf -m connect -t zmq

Example 8: Real-world usage of Redis as a transport::

    # in /etc/hosts
    192.168.0.10 redis-internal

    # /etc/beaver.conf
    [beaver]
    redis_url: redis://redis-internal:6379/0
    redis_namespace: app:unmappable

    # logstash indexer config:
    input {
      redis {
        host => 'redis-internal'
        data_type => 'list'
        key => 'app:unmappable'
        type => 'app:unmappable'
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver.conf -f /var/log/unmappable.log -t redis

As you can see, ``beaver`` is pretty flexible as to how you can use/abuse it in production.

Example 9: RabbitMQ connecting to defaults on remote broker::

    # /etc/beaver.conf
    [beaver]
    rabbitmq_host: 10.0.0.1

    # logstash indexer config:
    input { amqp {
        name => 'logstash-queue'
        type => 'direct'
        host => '10.0.0.1'
        exchange => 'logstash-exchange'
        key => 'logstash-key'
        exclusive => false
        durable => false
        auto_delete => false
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver.conf -t rabbitmq

Example 10: Read config from config.ini and put to stdout::

    # /etc/beaver.conf:
    [/tmp/somefile]
    type: mytype
    tags: tag1,tag2
    add_field: fieldname1,fieldvalue1[,fieldname2,fieldvalue2, ...]

    [/var/log/*log]
    type: syslog
    tags: sys

    [/var/log/{secure,messages}.log]
    type: syslog
    tags: sys

    # From the commandline
    beaver -c /etc/beaver.conf -t stdout

Example 11: UDP transport::

    # /etc/beaver.conf
    [beaver]
    udp_host: 127.0.0.1
    udp_port: 9999

    # logstash indexer config:
    input {
      udp {
        type => 'shipper-input'
        host => '127.0.0.1'
        port => '9999'
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver.conf -t udp

Todo
====

* More documentation
* Use python threading + subprocess in order to support usage of ``yield`` across all operating systems
* ~~Fix usage on non-linux platforms - file.readline() does not work as expected on OS X. See above for potential solution~~
* More transports
* ~~Ability to specify files, tags, and other metadata within a configuration file~~

Caveats
=======

When using ``copytruncate`` style log rotation, two race conditions can occur:

1. Any log data written prior to truncation which beaver has not yet
   read and processed is lost. Nothing we can do about that.

2. Should the file be truncated, rewritten, and end up being larger than
   the original file during the sleep interval, beaver won't detect
   this. After some experimentation, this behavior also exists in GNU
   tail, so I'm going to call this a "don't do that then" bug :)

   Additionally, the files beaver will most likely be called upon to
   watch which may be truncated are generally going to be large enough
   and slow-filling enough that this won't crop up in the wild.


Credits
=======

Based on work from Giampaolo and Lusis::

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
