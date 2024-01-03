import xml.etree.ElementTree as ET
from . import FormatterBase


class FormatterXML(FormatterBase):
    def format(self, record):
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        xml_begin = "<log>"
        xml_end = "</log>"
        xml_message = ""
        xml_message += xml_begin
        for key, value in message_dict.items():
            xml_message += f"<{key}>{value}</{key}>"
        xml_message += xml_end

        if self.pretty:
            parsed = ET.XML(xml_message)
            ET.indent(parsed)
            xml_message = ET.tostring(parsed, encoding="unicode")

        return xml_message
