
import os.path
import settings
import managers
import file_access

from utils.auxiliary import forfeit

from .auxiliary.constants import TYPE, APPLICATION, EXTENSION, TYPES
from .auxiliary import section, show, warn, detect, locate_repository, is_entity_name


def install(filename):
    entity = detect(filename)
    if not entity:
        warn("not an application or type: %s" % filename)
        return

    with section("install %s from %s" % (entity, filename), lazy=False):
        notifications = []
        try:
            if entity is TYPE:
                subject = managers.memory.install_type(filename=filename, into=notifications)
                if settings.STORE_BYTECODE:
                    subject.compile()
            elif entity is APPLICATION:
                subject = managers.memory.install_application(filename=filename, into=notifications)
                if settings.STORE_BYTECODE:
                    for library in subject.libraries.itervalues():
                        # show("precompile library %s" % library.name)
                        library.compile()

        except Exception as error:
            warn("unable to install %s: %s" % (entity, error))
            raise
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

    if is_entity_name(location):
        names = {filename[:-len(EXTENSION)]
            for filename in managers.file_manager.list(file_access.FILE, None, locate_repository(TYPE))
                if filename.endswith(EXTENSION)}
        location, query = None, location
        if query in names:
            location = locate_repository(type=query)
        else:
            for name in names:
                if name.startswith(query):
                    location = locate_repository(type=name)
        if not location:
            warn("no such type in the repository: %s" % query)
            return

    if os.path.isdir(location):
        with section("install types from %s" % location):
            for filename in managers.file_manager.list(file_access.FILE, None, location):
                if filename.endswith(EXTENSION):
                    install(os.path.join(location, filename))
    else:
        install(location)
