
from .auxiliary import query


REQUEST = "<action name=\"memorize\"/>"
RESPONSE = "<reply/>"


def run(address=None, port=None):
    """
    memorize server object's state
    :param address: specifies server address
    :key int port: specifies server port
    """
    message = query("memorize", address, port, REQUEST)
    if message != RESPONSE:
        raise Exception("Incorrect response")
