import argparse
import glob2
import itertools
import logging
import platform
import re
import sys

import beaver

logging.basicConfig()

MAGIC_BRACKETS = re.compile("({([^}]+)})")
REOPEN_FILES = 'linux' not in platform.platform().lower()


def parse_args():
    epilog_example = """
    Beaver provides an lightweight method for shipping local log
    files to Logstash. It does this using either redis, stdin,
    zeromq as the transport. This means you'll need a redis,
    stdin, zeromq input somewhere down the road to get the events.

    Events are sent in logstash's json_event format. Options can
    also be set as environment variables.

    Please see the readme for complete examples.
    """
    parser = argparse.ArgumentParser(description='Beaver logfile shipper', epilog=epilog_example, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--configfile', help='ini config file path', dest='config', default='/dev/null')
    parser.add_argument('-d', '--debug', help='enable debug mode', dest='debug', default=False, action='store_true')
    parser.add_argument('-D', '--daemonize', help='daemonize in the background', dest='daemonize', default=False, action='store_true')
    parser.add_argument('-f', '--files', help='space-separated filelist to watch, can include globs (*.log). Overrides --path argument', dest='files', default=None, nargs='+')
    parser.add_argument('-F', '--format', help='format to use when sending to transport', default=None, dest='format', choices=['json', 'msgpack', 'string', 'raw'])
    parser.add_argument('-H', '--hostname', help='manual hostname override for source_host', default=None, dest='hostname')
    parser.add_argument('-m', '--mode', help='bind or connect mode', dest='mode', default=None, choices=['bind', 'connect'])
    parser.add_argument('-l', '--logfile', '-o', '--output', help='file to pipe output to (in addition to stdout)', default=None, dest='output')
    parser.add_argument('-p', '--path', help='path to log files', default=None, dest='path')
    parser.add_argument('-P', '--pid', help='path to pid file', default=None, dest='pid')
    parser.add_argument('-t', '--transport', help='log transport method', dest='transport', default=None, choices=['rabbitmq', 'redis', 'stdout', 'zmq', 'udp'])
    parser.add_argument('-v', '--version', help='output version and quit', dest='version', default=False, action='store_true')
    parser.add_argument('--fqdn', help="use the machine's FQDN for source_host", dest="fqdn", default=False, action='store_true')

    return parser.parse_args()


def setup_custom_logger(name, args=None, output=None, formatter=None):
    logger = logging.getLogger(name)
    logger.propagate = False
    if logger.handlers:
        logger.handlers = []

    has_args = args is not None and type(args) == argparse.Namespace
    is_debug = has_args and args.debug == True

    if not logger.handlers:
        if formatter is None:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)-7s %(message)s')

        handler = logging.StreamHandler()
        if output is None and has_args and args.daemonize:
            output = args.output

        if output is not None:
            handler = logging.FileHandler(output)

        if formatter is not False:
            handler.setFormatter(formatter)

        logger.addHandler(handler)

    if is_debug:
        logger.setLevel(logging.DEBUG)
        if hasattr(logging, 'captureWarnings'):
            logging.captureWarnings(True)
    else:
        logger.setLevel(logging.INFO)
        if hasattr(logging, 'captureWarnings'):
            logging.captureWarnings(False)

    logger.debug('Logger level is {0}'.format(logging.getLevelName(logger.level)))

    return logger


def version(args):
    if args.version:
        formatter = logging.Formatter('%(message)s')
        logger = setup_custom_logger('beaver', args=args, formatter=formatter)
        logger.info('Beaver {0}'.format(beaver.__version__))
        sys.exit(0)


def eglob(path):
    """Like glob.glob, but supports "/path/**/{a,b,c}.txt" lookup"""
    fi = itertools.chain.from_iterable
    paths = expand_paths(path)
    return list(fi(glob2.iglob(d) for d in paths))


def expand_paths(path):
    """When given a path with brackets, expands it to return all permutations
       of the path with expanded brackets, similar to ant.

       >>> expand_paths("../{a,b}/{c,d}")
       ['../a/c', '../a/d', '../b/c', '../b/d']
       >>> expand_paths("../{a,b}/{a,b}.py")
       ['../a/a.py', '../a/b.py', '../b/a.py', '../b/b.py']
       >>> expand_paths("../{a,b,c}/{a,b,c}")
       ['../a/a', '../a/b', '../a/c', '../b/a', '../b/b', '../b/c', '../c/a', '../c/b', '../c/c']
       >>> expand_paths("test")
       ['test']
       >>> expand_paths("")
    """
    pr = itertools.product
    parts = MAGIC_BRACKETS.findall(path)
    if path == "":
        return
    elif not parts:
        return [path]

    permutations = [[(p[0], i, 1) for i in p[1].split(",")] for p in parts]
    return [_replace_all(path, i) for i in pr(*permutations)]


def _replace_all(path, replacements):
    for j in replacements:
        path = path.replace(*j)
    return path
