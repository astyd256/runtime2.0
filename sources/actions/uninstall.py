
import managers

from .auxiliary.constants import APPLICATION, TYPE, APPLICATIONS, TYPES
from .auxiliary import section, show, confirm, search


def uninstall(entity, subject):
    with section("uninstall %s" % subject, lazy=False):
        try:
            subject.uninstall()
        except Exception as error:
            show("unable to uninstall %s: %s" % (entity, error))


def run(identifier, yes=False):
    """
    uninstall application or type
    :param uuid_or_name identifier: application or type uuid or name or types to uninstall all types
    :param switch yes: assume positive answer to confirmation request
    """
    if identifier in APPLICATIONS:
        if yes or confirm("uninstall all applications"):
            for subject in tuple(managers.memory.applications.itervalues()):
                uninstall(APPLICATION, subject)
    elif identifier in TYPES:
        if yes or confirm("uninstall all types"):
            for subject in tuple(managers.memory.types.itervalues()):
                uninstall(TYPE, subject)
    else:
        entity, subject = search(identifier)
        if entity:
            uninstall(entity, subject)
        else:
            show("unable to find: %s" % identifier)
