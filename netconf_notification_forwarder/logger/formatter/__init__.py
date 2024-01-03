from .base import FormatterBase
from .xml import FormatterXML
from .json import FormatterJSON
from .raw import FormatterRAW


class FormatterStyle:
    # pseudo-enum
    XML = FormatterXML()
    PRETTY_XML = FormatterXML(pretty=True)
    JSON = FormatterJSON()
    PRETTY_JSON = FormatterJSON(pretty=True)
    RAW = FormatterRAW()
    PRETTY_RAW = FormatterRAW(pretty=True)
