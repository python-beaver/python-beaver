#!/usr/bin/env python

import argparse

import beaver

epilog_example = """
Logstash shipper provides an lightweight method for shipping local
log files to Logstash.
It does this using zeromq as the transport. This means you'll need
a zeromq input somewhere down the road to get the events.

Events are sent in logstash's json_event format.

Examples 1: Listening on port 5556 (all interfaces)
    cli: ZEROMQ_ADDRESS="tcp://*:5556" logstash-shipper -m bind -p /var/log/
    logstash config:
        input { zeromq {
            type => 'shipper-input'
            mode => 'client'
            topology => 'pushpull'
            address => 'tcp://shipperhost:5556'
          } }
        output { stdout { debug => true } }

Example 2: Connecting to remote port 5556 on indexer
    cli: ZEROMQ_ADDRESS="tcp://indexer:5556" logstash-shipper -m connect -p /var/log/
    logstash config:
        input { zeromq {
            type => 'shipper-input'
            mode => 'server'
            topology => 'pushpull'
            address => 'tcp://*:5556'
          }}
        output { stdout { debug => true } }

Example 3: Sending messages to a redis list
    cli: REDIS_URL="redis://localhost:6379/0" logstash-shipper -p /var/log/

"""
parser = argparse.ArgumentParser(description='Logstash logfile shipper',
                                epilog=epilog_example,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-r', '--run', help='run worker or interactive mode',
                    default='worker', choices=['worker', 'interactive'])
parser.add_argument('-m', '--mode', help='bind or connect mode',
                    default='bind', choices=['bind', 'connect'])
parser.add_argument('-p', '--path', help='path to log files', default="/var/log")
parser.add_argument('-f', '--files', help='comma-separated filelist to watch. Overrides --path argument', default=None, nargs='+')
parser.add_argument('-t', '--transport', help='log transport method', required=True)

args = parser.parse_args()

beaver.cli(args.run, args)
