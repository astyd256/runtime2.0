
import os.path
import managers
from logs import console
from .detecting import TYPE, EXTENSION, search


def export(entity, subject, location):
    console.write("export %s %s: %s to %s" % (entity, subject.id, subject.name, location))
    try:
        subject.export(location)
    except Exception as error:
        console.error("unable to export %s: %s" % (entity, error))
        raise


def run(identifier, location):
    """
    export application or type
    :param uuid_or_name identifier: uuid or name of application or type or "types"
    :param location: output file or directory
    """
    if identifier == "types":
        if not os.path.isdir(location):
            console.error("for exporting types location must be directory")
            return

        for subject in managers.memory.types.itervalues():
            export(TYPE, subject, os.path.join(location, subject.name + EXTENSION))
    else:
        if os.path.isdir(location):
            location = os.path.join(location, subject.name + EXTENSION)
        elif not location.endswith(EXTENSION):
            location += EXTENSION

        entity, subject = search(identifier)
        if entity:
            export(entity, subject, location)
