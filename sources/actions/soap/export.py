
from ..auxiliary import section, warn, autocomplete
from .auxiliary import soap_query, SOAPError


DEFAULT_ADDRESS = "localhost"
DEFAULT_USER = "root"

SOAP_EXPORT_METHOD = "export_application"


def run(identifier, location, address=None, user=None, password=None):
    """
    export application or type
    :param uuid identifier: uuid of application
    :param location: output file or directory
    :param address: remote server address (localhost by default)
    :param user: login user name (root by default)
    :param password: login password
    """
    if address is None:
        address = DEFAULT_ADDRESS
    if user is None:
        user = DEFAULT_USER
    if password is None:
        password = user

    with section("export application to %s" % location, lazy=False):
        try:
            data = soap_query("retrieve application from", address, user, password, identifier, SOAP_EXPORT_METHOD)
        except SOAPError as error:
            warn("unable to export: %s" % error)
            return

        with open(autocomplete(identifier, location), "wb") as file:
            file.write(data.encode("utf8"))
