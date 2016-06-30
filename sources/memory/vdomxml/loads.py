
from logs import log
from utils.parsing import Parser, ParsingException
from .builder import vdomxml_builder


def loads(vdomxml, application, profile=None):
    parser = Parser(builder=vdomxml_builder, lower=True, options=application, notify=True)
    try:
        object = parser.parse(vdomxml)
        if parser.report:
            log.warning("Loads VDOM XML notifications")
            for lineno, message in parser.report:
                log.warning("    %s at line %s" % (message, lineno))
        return object
    except ParsingException as error:
        raise Exception("Unable to parse VDOM XML, line %s: %s" % (error.lineno, error))
