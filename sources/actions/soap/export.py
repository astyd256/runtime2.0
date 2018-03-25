
from ..auxiliary import section, warn, autocomplete
from .auxiliary import soap_query, SOAPError


DEFAULT_ADDRESS = "localhost"
DEFAULT_USER = "root"


def run(identifier, location, address=None, user=None, password=None):
    """
    export application or type
    :arg uuid identifier: uuid of application
    :arg location: output file or directory
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

    with section("export remote application to %s" % location, lazy=False):
        try:
            data = soap_query("query", address, user, password, "export_application", application=identifier)
        except SOAPError as error:
            warn("unable to export: %s" % error)
            return

        with open(autocomplete(identifier, location), "wb") as file:
            file.write(data.encode("utf8"))
