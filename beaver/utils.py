import glob
import itertools
import logging
import os
import re
import warnings

_magic_brackets = re.compile("({([^}]+)})")


def setup_custom_logger(name, debug=False, formatter=None):
    if formatter is None:
        formatter = logging.Formatter('[%(asctime)s] %(levelname)-7s %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info('debug level is on')
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(handler)
    return logger


def check_for_deprecated_usage():
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
        warnings.warn('Deprecated use of ENV VAR: {0}'.format(deprecated_env_var_usage.join(', ')), DeprecationWarning)


def _replace_all(path, replacements):
    for j in replacements:
        path = path.replace(*j)
    return path


def eglob(path):
    """Like glob.glob, but supports "/path/**/{a,b,c}.txt" lookup"""
    fi = itertools.chain.from_iterable
    paths = expand_paths(path)
    return list(fi(glob.iglob(d) for d in paths))


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
    parts = _magic_brackets.findall(path)
    if path == "":
        return
    elif not parts:
        return [path]

    permutations = [[(p[0], i, 1) for i in p[1].split(",")] for p in parts]
    return [_replace_all(path, i) for i in pr(*permutations)]
