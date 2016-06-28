
import os.path

import managers
import file_access

from utils.auxiliary import forfeit

from .auxiliary import section, show
from .detecting import TYPE, APPLICATION, EXTENSION, detect


def install(filename):
    entity = detect(filename)
    if entity:
        with section("install %s from %s" % (entity, filename), instant=True):
            try:
                notifications = []
                if entity is TYPE:
                    subject = managers.memory.install_type(filename, into=notifications)
                elif entity is APPLICATION:
                    subject = managers.memory.install_application(filename, into=notifications)
            except Exception as error:
                show("unable to install %s: %s" % (entity, error))
                raise
            else:
                with section("notifications"):
                    for lineno, message in notifications:
                        show("line %d: %s" % (lineno, forfeit(message)))
                show("contains %s:%s" % (subject.id, subject.name.lower()))


def run(location):
    """
    install application or type
    :param location: input filename with application or type or directory to search
    """
    if os.path.isdir(location):
        with section("install everything from %s" % location):
            for filename in managers.file_manager.list(file_access.FILE, None, location):
                if filename.endswith(EXTENSION):
                    install(os.path.join(location, filename))
    else:
        install(location)
