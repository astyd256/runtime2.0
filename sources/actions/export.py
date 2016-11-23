
import os.path
import managers
from .auxiliary.constants import TYPE, APPLICATION, REPOSITORY, TYPES, APPLICATIONS
from .auxiliary import section, show, confirm, search, autocomplete, locate_repository


def export(entity, subject, location):
    with section("export %s to %s" % (subject, location), lazy=False):
        try:
            subject.export(location)
        except Exception as error:
            show("unable to export %s: %s" % (entity, error))


def run(identifier, location=None, yes=False):
    """
    export application or type
    :param uuid_or_name identifier: uuid or name of application or type or "types"
    :param location: output file or directory (repository by default)
    :param switch yes: assume positive answer to confirmation request
    """
    if identifier in TYPES:
        if location is None or location in REPOSITORY:
            location = locate_repository(TYPE)

        if not os.path.isdir(location):
            show("not a directory: %s" % location)
            return

        if yes or confirm("export all types"):
            for subject in managers.memory.types.itervalues():
                export(TYPE, subject, autocomplete(subject, location))
    elif identifier in APPLICATIONS:
        if location is None or location in REPOSITORY:
            location = locate_repository(APPLICATION)

        if not os.path.isdir(location):
            show("not a directory: %s" % location)
            return

        if yes or confirm("export all applications"):
            for subject in managers.memory.applications.itervalues():
                export(APPLICATION, subject, autocomplete(subject, location))
    else:
        entity, subject = search(identifier)
        if entity is None:
            show("not found: %s" % identifier)
            return

        if location is None or location in REPOSITORY:
            location = locate_repository(entity)

        export(entity, subject, autocomplete(subject, location))
