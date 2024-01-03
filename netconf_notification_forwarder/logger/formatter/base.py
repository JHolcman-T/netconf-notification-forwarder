import logging


class FormatterBase(logging.Formatter):
    def __init__(self, pretty: bool = False):
        self.fmt_dict = {
            "level": "levelname",
            "logger": "name",
            "timestamp": "asctime",
            "message": "message",
        }
        self.default_time_format = "%Y-%m-%dT%H:%M:%S"
        self.default_msec_format = "%s.%03dZ"
        self.datefmt = None
        self.pretty = pretty

    def usesTime(self) -> bool:
        """
        Overwritten to look for the attribute in the format dict values instead of the fmt string.
        """
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record) -> dict:
        """
        Overwritten to return a dictionary of the relevant LogRecord attributes instead of a string.
        KeyError is raised if an unknown attribute is provided in the fmt_dict.
        """
        return {fmt_key: record.__dict__[fmt_val] for fmt_key, fmt_val in self.fmt_dict.items()}

    def format(self, record):
        raise NotImplementedError
