
from ..auxiliary import section, warn, autocomplete
from .auxiliary import soap_query, SOAPError


DEFAULT_ADDRESS = "localhost"
DEFAULT_USER = "root"


def run(identifier=None, name=None, delete=False, address=None, user=None, password=None):
    """
    select application through soap
    :arg uuid identifier: uuid of application to select
    :key name: site name
    :key switch delete: delete association
    :param address: remote server address (localhost by default)
    :key user: login user name (root by default)
    :key password: login password
    """
    if delete:
        if identifier:
            warn("identifier is not allowed on delete: %s" % identifier)
            return
    else:
        if not identifier:
            warn("identifier is required")
            return

    if address is None:
        address = DEFAULT_ADDRESS
    if user is None:
        user = DEFAULT_USER
    if password is None:
        password = user

    with section("remote select %s for %s" % (identifier or "none", name or "default"), lazy=False):
        try:
            soap_query(
                "query", address, user, password,
                ("delete_application_vhost" if delete else "set_application_vhost"),
                name, application=identifier)
        except SOAPError as error:
            warn("unable to select: %s" % error)
            return
