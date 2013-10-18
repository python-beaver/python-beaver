.. image:: https://secure.travis-ci.org/josegonzalez/beaver.png
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

    pip install beaver==30

Usage
=====

usage::

    beaver [-h] [-c CONFIG] [-C CONFD_PATH] [-d] [-D] [-f FILES [FILES ...]]
           [-F {json,msgpack,raw,rawjson,string}] [-H HOSTNAME] [-m {bind,connect}]
           [-l OUTPUT] [-p PATH] [-P PID]
           [-t {mqtt,rabbitmq,redis,sqs,stdout,tcp,udp,zmq}] [-v] [--fqdn]

optional arguments::

    -h, --help            show this help message and exit
    -c CONFIG, --configfile CONFIG
                          main beaver ini config file path
    -C CONFD_PATH         ini config directory path
    -d, --debug           enable debug mode
    -D, --daemonize       daemonize in the background
    -f FILES [FILES ...], --files FILES [FILES ...]
                          space-separated filelist to watch, can include globs
                          (*.log). Overrides --path argument
    -F {json,msgpack,raw,rawjson,string}, --format {json,msgpack,raw,rawjson,string}
                          format to use when sending to transport
    -H HOSTNAME, --hostname HOSTNAME
                          manual hostname override for source_host
    -m {bind,connect}, --mode {bind,connect}
                          bind or connect mode
    -l OUTPUT, --logfile OUTPUT, -o OUTPUT, --output OUTPUT
                          file to pipe output to (in addition to stdout)
    -p PATH, --path PATH  path to log files
    -P PID, --pid PID     path to pid file
    -t {mqtt,rabbitmq,redis,stdout,tcp,udp,zmq}, --transport {mqtt,rabbitmq,redis,sqs,stdout,tcp,udp,zmq}
                          log transport method
    -v, --version         output version and quit
    --fqdn                use the machine's FQDN for source_host

Background
==========

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using redis, zeromq, tcp, udp, rabbit or stdout as the transport. This means you'll need a redis, zeromq, tcp, udp, amqp or stdin input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

NOTE: the redis transport uses a namespace of ``logstash:beaver`` by default.  You will need to update your logstash indexer to match this, or you may configure beaver to do otherwise.

Configuration File Options
--------------------------

Beaver can optionally get data from a ``configfile`` using the ``-c`` flag. This file is in ``ini`` format. Global configuration will be under the ``beaver`` stanza. The following are global beaver configuration keys with their respective meanings:

* mqtt_host: Default ``localhost``. Host for mosquitto
* mqtt_port: Default ``1883``. Port for mosquitto
* mqtt_clientid: Default ``mosquitto``. Mosquitto client id
* mqtt_keepalive: Default ``60``. mqtt keepalive ping
* mqtt_topic: Default ``/logstash``. Topic to publish to
* rabbitmq_host: Defaults ``localhost``. Host for RabbitMQ
* rabbitmq_port: Defaults ``5672``. Port for RabbitMQ
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
* sqs_aws_access_key: Can be left blank to use IAM Roles or AWS_ACCESS_KEY_ID environment variable (see: https://github.com/boto/boto#getting-started-with-boto)
* sqs_aws_secret_key: Can be left blank to use IAM Roles or AWS_SECRET_ACCESS_KEY environment variable (see: https://github.com/boto/boto#getting-started-with-boto)
* sqs_aws_region: Default ``us-east-1``. AWS Region
* sqs_aws_queue: SQS queue (must exist)
* tcp_host: Default ``127.0.0.1``. TCP Host
* tcp_port: Default ``9999``. TCP Port
* udp_host: Default ``127.0.0.1``. UDP Host
* udp_port: Default ``9999``. UDP Port
* zeromq_address: Default ``tcp://localhost:2120``. Zeromq URL
* zeromq_hwm: Default None. Zeromq HighWaterMark socket option
* zeromq_bind: Default ``bind``. Whether to bind to zeromq host or simply connect

The following are used for instances when a TransportException is thrown - Transport dependent

* respawn_delay: Default ``3``. Initial respawn delay for exponential backoff
* max_failure: Default ``7``. Max failures before exponential backoff terminates

The following configuration keys are for SinceDB support. Specifying these will enable saving the current line number in an sqlite database. This is useful for cases where you may be restarting the beaver process, such as during a logrotate.

* sincedb_path: Default ``None``. Full path to an ``sqlite3`` database. Will be created at this path if it does not exist. Beaver process must have read and write access

The following configuration keys are for building an SSH Tunnel that can be used to proxy from the current host to a desired server. This proxy is torn down when Beaver halts in all cases.

* ssh_key_file: Default ``None``. Full path to ``id_rsa`` key file
* ssh_tunnel: Default ``None``. SSH Tunnel in the format ``user@host:port``
* ssh_tunnel_port: Default ``None``. Local port for SSH Tunnel
* ssh_remote_host: Default ``None``. Remote host to connect to within SSH Tunnel
* ssh_remote_port: Default ``None``. Remote port to connect to within SSH Tunnel
* ssh_options: Default ``None``. Comma separated list of SSH options to Pass through to the SSH Tunnel. See ``ssh_config(5)`` for more options

The following configuration keys are for multi-line events support and are per file.

* multiline_regex_after: Default ``None``. If a line match this regular expression, it will be merged with next line(s).
* multiline_regex_before: Default ``None``. If a line match this regular expression, it will be merged with previous line(s).

The following can also be passed via argparse. Argparse will override all options in the configfile, when specified.

* format: Default ``json``. Options ``[ json, msgpack, string ]``. Format to use when sending to transport
* files: Default ``files``. Space-separated list of files to tail. (Comma separated if specified in the config file)
* path: Default ``/var/log``. Path glob to tail.
* transport: Default ``stdout``. Transport to use when log changes are detected
* fqdn: Default ``False``. Whether to use the machine's FQDN in transport output
* hostname: Default ``None``. Manually specified hostname

The following configuration key allows cleaning up the worker and transport sub-processes on an interval respawning

* refresh_worker_process: Default ``None``. Interval between sub-process cleanup

Examples
--------


Example 1: Listen to all files in the default path of /var/log on standard out as json::

    beaver

Example 2: Listen to all files in the default path of /var/log on standard out with msgpack::

    beaver --format msgpack

Example 3: Listen to all files in the default path of /var/log on standard out as a string::

    beaver --format string

Example 4: Sending logs from /var/log files to a redis list::

    # /etc/beaver/conf
    [beaver]
    redis_url: redis://localhost:6379/0

    # From the commandline
    beaver  -c /etc/beaver/conf -t redis

Example 5: Zeromq listening on port 5556 (all interfaces)::

    # /etc/beaver/conf
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
    beaver  -c /etc/beaver/conf -m bind -t zmq


Example 6: Zeromq connecting to remote port 5556 on indexer::

    # /etc/beaver/conf
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
    beaver -c /etc/beaver/conf -m connect -t zmq

Example 7: Real-world usage of Redis as a transport::

    # in /etc/hosts
    192.168.0.10 redis-internal

    # /etc/beaver/conf
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
    beaver -c /etc/beaver/conf -f /var/log/unmappable.log -t redis

Example 8: RabbitMQ connecting to defaults on remote broker::

    # /etc/beaver/conf
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
    beaver -c /etc/beaver/conf -t rabbitmq

Example 9: Read config from config.ini and put to stdout::

    # /etc/beaver/conf:
    ; follow a single file, add a type, some tags and fields
    [/tmp/somefile]
    type: mytype
    tags: tag1,tag2
    add_field: fieldname1,fieldvalue1[,fieldname2,fieldvalue2, ...]

    ; follow all logs in /var/log except those with `messages` or `secure` in the name.
    ; The exclude tag must be a valid python regular expression.
    [/var/log/*log]
    type: syslog
    tags: sys
    exclude: (messages|secure)

    ; follow /var/log/messages.log and /var/log/secure.log using file globbing
    [/var/log/{messages,secure}.log]
    type: syslog
    tags: sys

    # From the commandline
    beaver -c /etc/beaver/conf -t stdout

Example 10: TCP transport::

    # /etc/beaver/conf
    [beaver]
    tcp_host: 127.0.0.1
    tcp_port: 9999
    format: raw

    # logstash indexer config:
    input {
      tcp {
        host => '127.0.0.1'
        port => '9999'
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver/conf -t tcp

Example 11: UDP transport::

    # /etc/beaver/conf
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
    beaver -c /etc/beaver/conf -t udp

Example 12: SQS Transport::

    # /etc/beaver/conf
    [beaver]
    sqs_aws_region: us-east-1
    sqs_aws_queue: logstash-input
    sqs_aws_access_key: <access_key>
    sqs_aws_secret_key: <secret_key>

    # logstash indexer config:
    input {
      sqs {
        queue => "logstash-input"
        type => "shipper-input"
        format => "json_event"
        access_key => "<access_key>"
        secret_key => "<secret_key>"
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver/conf -t sqs

Example 13: [Raw Json Support](http://blog.pkhamre.com/2012/08/23/logging-to-logstash-json-format-in-nginx/::

    beaver --format rawjson

Example 14: Mqtt transport using Mosquitto::

    # /etc/beaver/conf
    [beaver]
    mqtt_client_id: 'beaver_client'
    mqtt_topic: '/logstash'
    mqtt_host: '127.0.0.1'
    mqtt_port: '1318'
    mqtt_keepalive: '60'

    # logstash indexer config:
    input {
      mqtt {
        host => '127.0.0.1'
        data_type => 'list'
        key => 'app:unmappable'
        type => 'app:unmappable'
      }
    }
    output { stdout { debug => true } }

    # From the commandline
    beaver -c /etc/beaver/conf -f /var/log/unmappable.log -t mqtt

Example 15: Sincedb support using and sqlite3 db

Note that this will require R/W permissions on the file at sincedb path, as Beaver will store the current line for a given filename/file id.::

    # /etc/beaver/conf
    [beaver]
    sincedb_path: /etc/beaver/since.db

    [/var/log/syslog]
    type: syslog
    tags: sys,main
    sincedb_write_interval: 3 ; time in seconds

    # From the commandline
    beaver -c /etc/beaver/conf

Example 16: Loading stanzas from /etc/beaver/conf.d/* support::

    # /etc/beaver/conf
    [beaver]
    format: json

    # /etc/beaver/conf.d/syslog
    [/var/log/syslog]
    type: syslog
    tags: sys,main

    # /etc/beaver/conf.d/nginx
    [/var/log/nginx]
    format: rawjson
    type: nginx
    tags: nginx,server

    # From the commandline
    beaver -c /etc/beaver/conf -C /etc/beaver/conf.d

Example 17: Simple multi-line event: if line is indented it is the continuation of an event::

    # /etc/beaver/conf
    [/tmp/somefile]
    multiline_regex_before = ^\s+


Example 18: Multi-line event for Python traceback::

    # /etc/beaver/conf
    [/tmp/python.log]
    multiline_regex_after = (^\s+File.*, line \d+, in)
    multiline_regex_before = (^Traceback \(most recent call last\):)|(^\s+File.*, line \d+, in)|(^\w+Error: )

    # /tmp/python.log
    DEBUG:root:Calling faulty_function
    WARNING:root:An error occured
    Traceback (most recent call last):
      File "doerr.py", line 12, in <module>
        faulty_function()
      File "doerr.py", line 7, in faulty_function
        0 / 0
    ZeroDivisionError: integer division or modulo by zero

Example 16: Use SSH options for redis transport through SSH Tunnel::

    # /etc/beaver/conf
    [beaver]
    transport: redis
    redis_url: redis://localhost:6379/0
    redis_namespace: logstash:beaver
    ssh_options: StrictHostKeyChecking=no, Compression=yes, CompressionLevel=9
    ssh_key_file: /etc/beaver/remote_key
    ssh_tunnel: remote-logger@logs.example.net
    ssh_tunnel_port: 6379
    ssh_remote_host: 127.0.0.1
    ssh_remote_port: 6379

As you can see, ``beaver`` is pretty flexible as to how you can use/abuse it in production.

Todo
====

* More documentation
* <del>Use python threading + subprocess in order to support usage of ``yield`` across all operating systems</del>
* <del>Fix usage on non-linux platforms - file.readline() does not work as expected on OS X. See above for potential solution</del>
* More transports
* <del>Ability to specify files, tags, and other metadata within a configuration file</del>

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

----

When you get an error similar to ``ImportError: No module named
_sqlite3`` your python seems to miss the sqlite3-module. This can be the
case on FreeBSD and probably other systems. If so, use the local package
manager or port system to build that module. On FreeBSD::

    cd /usr/ports/databases/py-sqlite3
    sudo make install clean

----

Binary data in your logs will be converted to escape sequences or ?'s depending on the encoding settings to prevent decoding exceptions from crashing beaver.

   | http://docs.python.org/2/library/codecs.html#codecs.replace_errors
   | malformed data is replaced with a suitable replacement character such as '?' in bytestrings and '\ufffd' in Unicode  strings.

Credits
=======

Based on work from Giampaolo and Lusis::

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
