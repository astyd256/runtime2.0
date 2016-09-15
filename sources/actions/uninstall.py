
import managers

from .auxiliary.constants import TYPE, TYPES
from .auxiliary import section, show, confirm, search


def uninstall(entity, subject):
    with section("uninstall %s" % subject, lazy=False):
        try:
            subject.uninstall()
        except Exception as error:
            show("unable to uninstall %s: %s" % (entity, error))


def run(identifier):
    """
    uninstall application or type
    :param uuid_or_name identifier: application or type uuid or name or types to uninstall all types
    """
    if identifier in TYPES:
        if confirm("uninstall all types"):
            for subject in tuple(managers.memory.types.itervalues()):
                uninstall(TYPE, subject)
    else:
        entity, subject = search(identifier)
        if entity:
            uninstall(entity, subject)
        else:
            show("unable to find: %s" % identifier)
