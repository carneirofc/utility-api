import logging


def get_logger(name=__file__, level=logging.INFO):
    """Returns a logger object"""

    logger = logging.getLogger(name)

    if not len(logger.handlers):
        logger.setLevel(logging.INFO)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(name)s [%(levelname)s] %(message)s")
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger
