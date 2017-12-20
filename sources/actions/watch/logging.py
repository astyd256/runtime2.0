
from utils.parsing import VALUE, Parser
from logs.levels import LEVEL_TO_NAME
from ..auxiliary import show
from .auxiliary import query


REQUEST = "<action name=\"logging\"/>"
REQUEST_LEVEL = "<action name=\"logging\"><option name=\"level\">%s</option></action>"


def builder(parser):

    def reply():

        def error():
            message = yield VALUE
            raise Exception(message)

        def logging():

            def level():
                value = yield VALUE
                parser.accept(value)

            yield level

        return error, logging

    return reply


def run(level=None, address=None, port=None, timeout=None):
    """
    logging status and options
    :param log_level level: specifies desired log level
    """
    if level is None:
        request = REQUEST
    else:
        request = REQUEST_LEVEL % LEVEL_TO_NAME[level].lower()

    message = query("watch logging", address, port, request, timeout=timeout)

    level = Parser(builder=builder, notify=True, supress=True).parse(message)
    if level is None:
        show("unable to get level")
    else:
        show("log level is %s" % level)
