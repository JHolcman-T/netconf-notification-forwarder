from . import FormatterBase


class FormatterRAW(FormatterBase):
    def format(self, record) -> str:
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)
        message_dict["level"] = f"<{message_dict['level']}>"

        if self.pretty:
            message = f"%(level)-10s  %(timestamp)s  (%(logger)s): %(message)s"
        else:
            message = f"%(level)s  %(timestamp)s  %(logger)s  %(message)s"

        return message % message_dict
