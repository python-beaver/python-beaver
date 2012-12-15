======
Beaver
======

python daemon that munches on logs and sends their contents to logstash

Requirements
============

* Python 2.7 (untested on other versions)
* Optional zeromq support: install libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``) and pyzmq (``pip install pyzmq==2.1.11``)

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/beaver.git#egg=beaver

From PyPI::

    pip install beaver==10

Usage
=====

usage::

    beaver [-h] [-m {bind,connect}] [-p PATH] [-f FILES [FILES ...]]
              [-t {rabbitmq,redis,stdout,zmq,udp}] [-c CONFIG] [-d DEBUG]

optional arguments::

    -h, --help            show this help message and exit
    -m {bind,connect}, --mode {bind,connect}
                        bind or connect mode
    -p PATH, --path PATH  path to log files
    -f FILES [FILES ...], --files FILES [FILES ...]
                        space-separated filelist to watch, can include globs
                        (*.log). Overrides --path argument
    -t {rabbitmq,redis,stdout,zmq}, --transport {rabbitmq,redis,stdout,zmq}
                        log transport method
    -c CONFIG, --configfile CONFIG
                        ini config file path
    -d DEBUG, --debug DEBUG
                        enable debug mode

Background
==========

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using either redis, stdin, zeromq as the transport. This means you'll need a redis, stdin, zeromq input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

NOTE: the redis transport uses a namespace of ``logstash:beaver`` by default.  You will need to update your logstash indexer to match this.

Examples
--------

Example 1: Listen to all files in the default path of /var/log on standard out as json::

    beaver

Example 2: Listen to all files in the default path of /var/log on standard out with msgpack::

    BEAVER_FORMAT='msgpack' beaver

Example 3: Listen to all files in the default path of /var/log on standard out as a string::

    BEAVER_FORMAT='string' beaver

Example 4: Sending logs from /var/log files to a redis list::

    REDIS_URL='redis://localhost:6379/0' beaver -t redis

Example 5: Use environment variables to send logs from /var/log files to a redis list::

    REDIS_URL='redis://localhost:6379/0' BEAVER_PATH='/var/log' BEAVER_TRANSPORT=redis beaver

Example 6: Zeromq listening on port 5556 (all interfaces)::

    ZEROMQ_ADDRESS='tcp://*:5556' beaver -m bind -t zmq

    # logstash config:
    input {
      zeromq {
        type => 'shipper-input'
        mode => 'client'
        topology => 'pushpull'
        address => 'tcp://shipperhost:5556'
      }
    }
    output { stdout { debug => true } }

Example 7: Zeromq connecting to remote port 5556 on indexer::

    ZEROMQ_ADDRESS='tcp://indexer:5556' beaver -m connect -t zmq

    # logstash config:
    input {
      zeromq {
        type => 'shipper-input'
        mode => 'server'
        topology => 'pushpull'
        address => 'tcp://*:5556'
      }
    }
    output { stdout { debug => true } }

Example 8: Real-world usage of Redis as a transport::

    # in /etc/hosts
    192.168.0.10 redis-internal

    # From the commandline
    REDIS_NAMESPACE='app:unmappable' REDIS_URL='redis://redis-internal:6379/0' beaver -f /var/log/unmappable.log -t redis

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

As you can see, ``beaver`` is pretty flexible as to how you can use/abuse it in production.

Example 9: RabbitMQ connecting to defaults on remote broker::

    # From the commandline
    RABBITMQ_HOST='10.0.0.1' beaver -t rabbitmq

    # logstash config:
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

Example 10: Read config from config.ini and put to stdout::

    # From the commandline
    beaver -c config.ini -t stdout

    # config.ini content:
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

Example 11: UDP transport::

    # From the commandline
    UDP_HOST='127.0.0.1' UDP_PORT='9999' beaver -t udp

    # logstash config:
    input {
      udp {
        type => 'shipper-input'
        host => '127.0.0.1'
        port => '9999'
      }
    }
    output { stdout { debug => true } }

Todo
====

* Use python threading + subprocess in order to support usage of ``yield`` across all operating systems
* Fix usage on non-linux platforms - file.readline() does not work as expected on OS X. See above for potential solution
* More transports
* ~Ability to specify files, tags, and other metadata within a configuration file~

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
