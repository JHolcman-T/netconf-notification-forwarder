import logging
import logging.config
import sys
from .formatter import FormatterStyle


def _handlers():
    handlers = [logging.StreamHandler(sys.stdout)]
    # set formatter
    for handler in handlers:
        handler.setFormatter(FormatterStyle.PRETTY_JSON)
    return handlers


_logger_names = []


def get_logger(name: str = None):
    logger = logging.getLogger(name)
    if name not in _logger_names:
        logger.level = logging.DEBUG
        for handler in _handlers():
            logger.addHandler(handler)
    return logger
