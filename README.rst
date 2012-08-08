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
    -t {amqp,redis,stdout}, --transport {amqp,redis,stdout}
                      log transport method

Background
==========

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using either redis, stdin, zeromq as the transport. This means you'll need a redis, stdin, zeromq input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

Examples
--------

Example 1: Listen to all files in the default path of /var/log on standard out::

    beaver

Example 2: Sending logs from /var/log files to a redis list::

    REDIS_URL="redis://localhost:6379/0" beaver -t redis

Example 3: Use environment variables to send logs from /var/log files to a redis list::

    REDIS_URL="redis://localhost:6379/0" BEAVER_PATH="/var/log" BEAVER_TRANSPORT=redis beaver

Example 4: Zeromq listening on port 5556 (all interfaces)::

    ZEROMQ_ADDRESS="tcp://*:5556" beaver -m bind

    # logstash config:
    input { zeromq {
        type => 'shipper-input'
        mode => 'client'
        topology => 'pushpull'
        address => 'tcp://shipperhost:5556'
      } }
    output { stdout { debug => true } }

Example 5: Zeromq connecting to remote port 5556 on indexer::

    ZEROMQ_ADDRESS="tcp://indexer:5556" beaver -m connect

    # logstash config:
    input { zeromq {
        type => 'shipper-input'
        mode => 'server'
        topology => 'pushpull'
        address => 'tcp://*:5556'
      }}
    output { stdout { debug => true } }

Example 6: Real-world usage of Redis as a transport::

    # in /etc/hosts
    192.168.0.10 redis-internal

    # From the commandline
    REDIS_NAMESPACE='app:unmappable' REDIS_URL='redis://redis-internal:6379/0' beaver -f /var/log/unmappable.log -t redis

    # logstash indexer config:
    redis {
        host => 'redis-internal' # this is in dns for work
        data_type => 'list'
        key => 'app:unmappable'
        type => 'app:unmappable'
    }

As you can see, ``beaver`` is pretty flexible as to how you can use/abuse it in production.

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