
import os.path
import managers
import file_access

from utils.auxiliary import forfeit

from .auxiliary.constants import TYPE, APPLICATION, EXTENSION, TYPES
from .auxiliary import section, show, detect, locate_repository


def install(filename):
    entity = detect(filename)
    if not entity:
        show("not an application or type: %s" % filename)
        return

    with section("install %s from %s" % (entity, filename), lazy=False):
        notifications = []
        try:
            if entity is TYPE:
                subject = managers.memory.install_type(filename, into=notifications)
            elif entity is APPLICATION:
                subject = managers.memory.install_application(filename, into=notifications)
        except Exception as error:
            show("unable to install %s: %s" % (entity, error))
        else:
            show("contains %s" % subject)
            with section("notifications"):
                for lineno, message in notifications:
                    show("line %d: %s" % (lineno, forfeit(message)))


def run(location):
    """
    install application or type
    :param location: input filename with application or type or directory to search
    """
    if location in TYPES:
        location = locate_repository(TYPE)

    if os.path.isdir(location):
        with section("install types from %s" % location):
            for filename in managers.file_manager.list(file_access.FILE, None, location):
                if filename.endswith(EXTENSION):
                    install(os.path.join(location, filename))
    else:
        install(location)
