======
Beaver
======

python daemon that munches on logs and sends their contents to logstash

Requirements
============

* Python 2.7 (untested on other versions)
* libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``)

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/beaver.git#egg=beaver

From PyPI::

    pip install beaver==1

Usage
=====

usage::

    beaver [-h] [-r {worker,interactive}] [-m {bind,connect}] [-p PATH]
                     [-f FILES [FILES ...]] [-t TRANSPORT]

optional arguments::

    -h, --help            show this help message and exit
    -m {bind,connect}, --mode {bind,connect}
                          bind or connect mode
    -p PATH, --path PATH  path to log files
    -f FILES [FILES ...], --files FILES [FILES ...]
                          space-separated filelist to watch. Overrides --path
                          argument
    -t {rabbitmq,redis,stdout,zmq}, --transport {rabbitmq,redis,stdout,zmq}
                          log transport method
    -c CONFIG, --configfile CONFIG
                          ini config file path
Background
==========

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using either redis, stdin, zeromq as the transport. This means you'll need a redis, stdin, zeromq input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

Examples
--------

Example 1: Listen to all files in the default path of /var/log on standard out as json::

    beaver

Example 2: Listen to all files in the default path of /var/log on standard out with msgpack::

    BEAVER_FORMAT='msgpack' beaver

Example 3: Listen to all files in the default path of /var/log on standard out as a string::

    BEAVER_FORMAT='string' beaver

Example 4: Sending logs from /var/log files to a redis list::

    REDIS_URL="redis://localhost:6379/0" beaver -t redis

Example 5: Use environment variables to send logs from /var/log files to a redis list::

    REDIS_URL="redis://localhost:6379/0" BEAVER_PATH="/var/log" BEAVER_TRANSPORT=redis beaver

Example 6: Zeromq listening on port 5556 (all interfaces)::

    ZEROMQ_ADDRESS="tcp://*:5556" beaver -m bind

    # logstash config:
    input { zeromq {
        type => 'shipper-input'
        mode => 'client'
        topology => 'pushpull'
        address => 'tcp://shipperhost:5556'
      } }
    output { stdout { debug => true } }

Example 7: Zeromq connecting to remote port 5556 on indexer::

    ZEROMQ_ADDRESS="tcp://indexer:5556" beaver -m connect

    # logstash config:
    input { zeromq {
        type => 'shipper-input'
        mode => 'server'
        topology => 'pushpull'
        address => 'tcp://*:5556'
      }}
    output { stdout { debug => true } }

Example 8: Real-world usage of Redis as a transport::

    # in /etc/hosts
    192.168.0.10 redis-internal

    # From the commandline
    REDIS_NAMESPACE='app:unmappable' REDIS_URL='redis://redis-internal:6379/0' beaver -f /var/log/unmappable.log -t redis

    # logstash indexer config:
    input { redis {
        host => 'redis-internal' # this is in dns for work
        data_type => 'list'
        key => 'app:unmappable'
        type => 'app:unmappable'
    }}
    output { stdout { debug => "true" }}

As you can see, ``beaver`` is pretty flexible as to how you can use/abuse it in production.

Example 9: RabbitMQ connecting to defaults on remote broker::

    # From the commandline
    RABBITMQ_HOST="10.0.0.1" beaver -t rabbitmq

    # logstash config:
    input { amqp {
        name => "logstash-queue"
        type => "direct"
        host => "10.0.0.1"
        exchange => "logstash-exchange"
        key => "logstash-key"
        exclusive => false
        durable => false
        auto_delete => false
      }}
    output { stdout { debug => "true" }}


Example 10: Read config from config.ini and put to stdout::

    # From the commandline
    beaver -c config.ini -t stdout

    # config.ini content:
    [/tmp/somefile]
    type: mytype
    tags: tag1,tag2

    [/var/log/*log]
    type: syslog
    tags: sys

Todo
====

* Use python threading + subprocess in order to support usage of ``yield`` across all operating systems
* Fix usage on non-linux platforms - file.readline() does not work as expected on OS X. See above for potential solution
* More transports
* ~Separate tranports into different files so that individual transport requirements are not required on all installations (libzmq)~
* ~Create a python package~
* Ability to specify files, tags, and other  metadata within a configuration file

Credits
=======

Based on work from Giampaolo and Lusis::

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
