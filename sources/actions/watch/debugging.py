
from utils.parsing import VALUE, Parser
from ..auxiliary import show
from .auxiliary import query


REQUEST = "<action name=\"debugging\"/>"
REQUEST_STATUS = "<action name=\"debugging\"><option name=\"show-page-debug\">%s</option></action>"


def builder(parser):

    def reply():

        def error():
            message = yield VALUE
            raise Exception(message)

        def debugging():

            def show_page_debug():
                value = yield VALUE
                parser.accept(value == "enabled")

            yield show_page_debug

        return error, debugging

    return reply


def run(showpagedebug=None, address=None, port=None, timeout=None):
    """
    debugging status and options
    :param enable_or_disable showpagedebug: specifies desired status for page debug
    """
    if showpagedebug is None:
        request = REQUEST
    else:
        request = REQUEST_STATUS % ("enable" if showpagedebug else "disable")
    message = query("watch debugging", address, port, request, timeout=timeout)

    status = Parser(builder=builder, notify=True, supress=True).parse(message)
    if status is None:
        show("unable to get status")
    else:
        show("show page debug is %s" % ("enabled" if status else "disabled"))
