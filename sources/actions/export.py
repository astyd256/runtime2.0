
import os.path

import managers

from .auxiliary import section, show
from .detecting import TYPE, EXTENSION, search


def export(entity, subject, location):
    with section("export %s %s: %s to %s" % (entity, subject.id, subject.name, location), instant=True):
        try:
            subject.export(location)
        except Exception as error:
            show("unable to export %s: %s" % (entity, error))
            raise


def run(identifier, location):
    """
    export application or type
    :param uuid_or_name identifier: uuid or name of application or type or "types"
    :param location: output file or directory
    """
    if identifier == "types":
        if os.path.isdir(location):
            for subject in managers.memory.types.itervalues():
                export(TYPE, subject, os.path.join(location, subject.name + EXTENSION))
        else:
            show("for exporting types location must be directory")
    else:
        if os.path.isdir(location):
            location = os.path.join(location, subject.name + EXTENSION)
        elif not location.endswith(EXTENSION):
            location += EXTENSION

        entity, subject = search(identifier)
        if entity:
            export(entity, subject, location)
