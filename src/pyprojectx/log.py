import logging

logger = logging.getLogger(__name__)


def set_verbosity(verbosity: int):
    if verbosity == 1:
        logging.getLogger().setLevel(logging.INFO)
    if verbosity > 1:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    logging.basicConfig()
