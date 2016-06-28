
import os.path

import settings
import managers
import file_access

from .auxiliary import section, show
from .install import run as install


LOCATIONS = (
    ("applications", (file_access.APPLICATION, None)),
    ("types", (file_access.TYPE, None)),
    ("cache", (file_access.CACHE, None)),
    ("resources", (file_access.RESOURCE, None)),
    ("data", (file_access.FILE, None, settings.DATA_LOCATION)),
    ("databases", (file_access.DATABASE, None)),
    ("storage", (file_access.STORAGE, None)),
    ("temp", (file_access.FILE, None, settings.TEMPORARY_LOCATION)))


def run():
    """
    deploy runtime on the system
    """
    with section("initialize directories"):
        for caption, segments in LOCATIONS:
            show(caption)
            managers.file_manager.prepare_directory(*segments, cleanup=False)

    install(os.path.join(settings.REPOSITORY_LOCATION, settings.REPOSITORY_TYPES_DIRECTORY))
