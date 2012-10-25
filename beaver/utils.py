import logging


def setup_custom_logger(name, debug=False):
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
