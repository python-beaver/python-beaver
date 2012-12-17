import glob
import itertools
import logging
import re

logging.basicConfig()
_magic_brackets = re.compile("({([^}]+)})")


def setup_custom_logger(name, debug=False, formatter=None):
    logger = logging.getLogger()
    if logger.handlers:
        logger.handlers = []

    if not logger.handlers:
        if formatter is None:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)-7s %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if debug:
        logger.setLevel(logging.DEBUG)
        logger.info('Debug level is on')
        logging.captureWarnings(True)
    else:
        logger.setLevel(logging.INFO)
        logger.info('Info level is on')
        logging.captureWarnings(False)

    return logger


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
