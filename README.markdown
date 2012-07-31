# Beaver

python daemon that munches on logs and sends their contents to logstash

## Background

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using either redis, stdin, zeromq as the transport. This means you'll need a redis, stdin, zeromq input somewhere down the road to get the events.

Events are sent in logstash's json_event format.

Examples 1: Listening on port 5556 (all interfaces)

    cli: ZEROMQ_ADDRESS="tcp://*:5556" python beaver.py -m bind -p /var/log/ -t amqp
    logstash config:
        input { zeromq {
            type => 'shipper-input'
            mode => 'client'
            topology => 'pushpull'
            address => 'tcp://shipperhost:5556'
          } }
        output { stdout { debug => true } }

Example 2: Connecting to remote port 5556 on indexer

    cli: ZEROMQ_ADDRESS="tcp://indexer:5556" python beaver.py -m connect -p /var/log/ -t amqp
    logstash config:
        input { zeromq {
            type => 'shipper-input'
            mode => 'server'
            topology => 'pushpull'
            address => 'tcp://*:5556'
          }}
        output { stdout { debug => true } }

Example 3: Sending messages to a redis list

    cli: REDIS_URL="redis://localhost:6379/0" python beaver.py -p /var/log/ -t redis

## Todo

- Use python threading + subprocess in order to support usage of `yield` across all operating systems
- Fix usage on non-linux platforms - file.readline() does not work as expected on OS X. See above for potential solution
- More transports
- Ability to specify files, tags, and other  metadata within a configuration file

## Credits

Based on work from Giampaolo and Lusis:

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
