
from logs import console
from utils.parsing import VALUE, Parser
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


def run(status=None, address=None, port=None, timeout=None):
    """
    profiling status and options
    :param enable_or_disable status: specifies desired status
    """

    try:
        if status is None:
            request = REQUEST
        else:
            request = REQUEST_STATUS % ("enable" if status else "disable")

        message = query("watch profiling", address, port, request, timeout=timeout)

        status = Parser(builder=builder, notify=True, supress=True).parse(message)
        if status is None:
            console.write("unable to get status")
        else:
            console.write("profiling is %s" % ("enabled" if status else "disabled"))

    except Exception as error:
        console.error(error)
