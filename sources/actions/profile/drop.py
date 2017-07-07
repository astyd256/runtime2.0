
import settings
import managers
import file_access

from ..auxiliary import show


def run(name=None):
    """
    drop last profile
    :param name: specifies profile name
    """

    if name:
        locations = (settings.PROFILE_FILENAME_TEMPLATE % name,)
        if not managers.file_manager.exists(file_access.FILE, None, locations[0]):
            show("no profile")
            return
    else:
        locations = managers.file_manager.list(file_access.FILE, None, settings.PROFILE_LOCATION,
            pattern="*.%s" % settings.PROFILE_EXTENSION)
        if not locations:
            show("no profile")
            return

    show("drop profile%s" % "s" if len(locations) > 1 else "")
    for location in locations:
        managers.file_manager.delete(file_access.FILE, None, location)
