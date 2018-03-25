
from .auxiliary import query

ALIAS = "raise"

REQUEST = "<action name=\"intrude\"><option name=\"raise\"/><option name=\"thread\">%s</option></action>"
REQUEST_EXCEPTION = "<action name=\"intrude\"><option name=\"raise\">%s</option><option name=\"thread\">%s</option></action>"
RESPONSE = "<reply/>"


def run(thread, exception=None, address=None, port=None, timeout=None):
    """
    raise exception
    :arg thread thread: specifies thread name or identifier
    :key exception exception: specifies exception class
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    """

    if exception is None:
        request = REQUEST % thread
    else:
        request = REQUEST_EXCEPTION(exception, thread)

    message = query("raise", address, port, request, timeout=timeout)
    if message != RESPONSE:
        raise Exception("Incorrect response")
