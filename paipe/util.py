import logging

logger = logging.getLogger('paipe')
logger.addHandler(logging.StreamHandler())


def set_verbose(verbose: bool):
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)