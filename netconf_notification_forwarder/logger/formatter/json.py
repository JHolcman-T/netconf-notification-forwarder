from . import FormatterBase
import json


class FormatterJSON(FormatterBase):
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return json.JSONEncoder.default(self, obj)

    def format(self, record) -> str:
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        try:
            message = message_dict["message"]
            parsed = eval(message)
            assert isinstance(parsed, dict)
            message_dict["message"] = parsed
        except (SyntaxError, AssertionError):
            pass

        return (
            json.dumps(message_dict, ensure_ascii=False, indent=2, cls=self.SetEncoder)
            if self.pretty
            else json.dumps(message_dict, ensure_ascii=False, cls=self.SetEncoder)
        )
