import os

import file_access
import managers
import settings
from utils.auxiliary import forfeit

from . import uninstall, install
from .auxiliary import section, show, warn, detect, locate_repository, is_entity_name
from .auxiliary.constants import TYPE, APPLICATION, EXTENSION, TYPES
from .select import select as select_default


def update(filename, select=False):
    entity = detect(filename)
    if not entity:
        warn("not an application or type: %s" % filename)
        return

    with section("update %s from %s" % (entity, filename), lazy=False):
        notifications = []
        try:
            if entity is TYPE:
                uninstall.run(filename, select)
                install.run(filename, select)
            elif entity is APPLICATION:
                subject = managers.memory.update_application(filename)
                if settings.STORE_BYTECODE:
                    for library in subject.libraries.itervalues():
                        library.compile()
        except Exception as error:
            warn("unable to update %s: %s" % (entity, error))
            raise
        else:
            show("contains %s" % subject)
            with section("notifications"):
                for lineno, message in notifications:
                    show("line %d: %s" % (lineno, forfeit(message)))
            if select:
                if entity is not APPLICATION:
                    raise Exception("can't select non-application")
                select_default(subject)


def run(filename, select=False):
    """
    reinstall application or type
    :arg filename: input filename with application or type or directory to search
    :key switch select: select application as default
    """
    if filename in TYPES:
        filename = locate_repository(TYPE)

    if is_entity_name(filename):
        names = {
            filename[:-len(EXTENSION)]
            for filename in managers.file_manager.list(file_access.FILE, None, locate_repository(TYPE))
            if filename.endswith(EXTENSION)
        }
        filename, query = None, filename
        if query in names:
            filename = locate_repository(type=query)
        else:
            for name in names:
                if name.startswith(query):
                    filename = locate_repository(type=name)
        if not filename:
            warn("no such type in the repository: %s" % query)
            return

    if os.path.isdir(filename):
        with section("update types from %s" % filename):
            for filename in managers.file_manager.list(file_access.FILE, None, filename):
                if filename.endswith(EXTENSION):
                    update(os.path.join(filename, filename), select=select)
    else:
        update(filename, select=select)
