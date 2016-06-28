
import managers
from logs import console
from .auxiliary import confirm
from .detecting import TYPE, search


def uninstall(entity, subject):
    console.write("uninstall %s %s: %s" % (entity, subject.id, subject.name.lower()))
    try:
        subject.uninstall()
    except Exception as error:
        console.error("unable to uninstall %s: %s" % (entity, error))
        raise


def run(identifier):
    """
    uninstall application or type
    :param uuid_or_name identifier: application or type uuid or name or types to uninstall all types
    """
    if identifier == "types":
        if confirm("uninstall all types"):
            for subject in tuple(managers.memory.types.itervalues()):
                uninstall(TYPE, subject)
    else:
        entity, subject = search(identifier)
        if entity:
            uninstall(entity, subject)
