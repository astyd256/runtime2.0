
from ..auxiliary import section, warn, autocomplete
from .auxiliary import soap_query, SOAPError


DEFAULT_ADDRESS = "localhost"
DEFAULT_USER = "root"


def run(address=None, user=None, password=None):
    """
    soap ping
    :param address: remote server address (localhost by default)
    :key user: login user name (root by default)
    :key password: login password
    """
    if address is None:
        address = DEFAULT_ADDRESS
    if user is None:
        user = DEFAULT_USER
    if password is None:
        password = user

    try:
        soap_query("ping", address, user, password, "keep_alive")
    except SOAPError as error:
        warn("unable to ping: %s" % error)
        return
