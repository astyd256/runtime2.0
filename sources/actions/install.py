
import os.path
import managers
import file_access
from logs import console
from .detecting import TYPE, APPLICATION, EXTENSION, detect


def install(filename):
    entity = detect(filename)
    if entity:
        console.write("install %s from %s" % (entity, filename))
        try:
            if entity is TYPE:
                subject = managers.memory.install_type(filename)
            elif entity is APPLICATION:
                subject = managers.memory.install_application(filename)
        except Exception as error:
            console.error("unable to install %s: %s" % (entity, error))
        else:
            console.write("contains %s:%s" % (subject.id, subject.name.lower()))


def run(location):
    """
    install application or type
    :param location: input filename with application or type or directory to search
    """
    if os.path.isdir(location):
        console.write("install from %s" % location)
        for filename in managers.file_manager.list(file_access.FILE, None, location):
            if filename.endswith(EXTENSION):
                install(os.path.join(location, filename))
    else:
        install(location)
