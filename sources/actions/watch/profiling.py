
from utils.parsing import VALUE, Parser
from ..auxiliary import show
from .auxiliary import query


REQUEST = "<action name=\"profiling\"/>"
REQUEST_STATUS = "<action name=\"profiling\"><option name=\"status\">%s</option></action>"


def builder(parser):

    def reply():

        def error():
            message = yield VALUE
            raise Exception(message)

        def profiling():

            def status():
                value = yield VALUE
                parser.accept(value == "enabled")

            yield status

        return error, profiling

    return reply


def run(status=None, enable=False, disable=False, address=None, port=None, timeout=None):
    """
    profiling status and options
    :param enable_or_disable status: specifies desired status
    :param switch enable: enable profiling
    :param switch disable: disable profiling
    """
    if status is not None:
        request = REQUEST_STATUS % ("enable" if status else "disable")
    elif enable:
        request = REQUEST_STATUS % "enable"
    elif disable:
        request = REQUEST_STATUS % "disable"
    else:
        request = REQUEST
    message = query("watch profiling", address, port, request, timeout=timeout)

    status = Parser(builder=builder, notify=True, supress=True).parse(message)
    if status is None:
        show("unable to get status")
    else:
        show("profiling is %s" % ("enabled" if status else "disabled"))
