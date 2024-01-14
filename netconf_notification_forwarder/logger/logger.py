import logging
import logging.config
import sys
from .formatter import FormatterStyle


_formatter = FormatterStyle.PRETTY_JSON
_level = logging.DEBUG
_logger_names = []


def _handlers():
    global _formatter
    handlers = [logging.StreamHandler(sys.stdout)]
    # set formatter
    for handler in handlers:
        handler.setFormatter(_formatter)
    return handlers


def get_logger(name: str = None):
    global _logger_names
    logger = logging.getLogger(name)
    if name not in _logger_names:
        logger.level = logging.DEBUG
        for handler in _handlers():
            logger.addHandler(handler)
    return logger


def set_style(style: str):
    global _formatter
    string_to_class = {
        "raw": FormatterStyle.RAW,
        "pretty_raw": FormatterStyle.PRETTY_RAW,
        "xml": FormatterStyle.XML,
        "pretty_xml": FormatterStyle.PRETTY_XML,
        "json": FormatterStyle.JSON,
        "pretty_json": FormatterStyle.PRETTY_JSON,
    }
    formatter = string_to_class.get(style, False)
    if formatter is False:
        print(f"Bad log style! Got={style} but should be one of {list(string_to_class.keys())}", file=sys.stderr)
        exit(-1)
    _formatter = formatter


def set_level(level: str):
    global _level
    levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    log_level = levels.get(level, False)
    if log_level is False:
        print(f"Bad log level! Got={level} but should be one of {list(levels.keys())}", file=sys.stderr)
        exit(-1)
    _level = log_level
