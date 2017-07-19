
from .auxiliary import query


REQUEST = "<action name=\"ping\"/>"
RESPONSE = "<reply/>"


def run(address=None, port=None, timeout=None, udp=False):
    """
    ping server
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    :param switch udp: use UDP as transport protocol
    """
    message = query("ping", address, port, REQUEST, timeout=timeout, datagrams=udp)
    if message != RESPONSE:
        raise Exception("Incorrect response")
