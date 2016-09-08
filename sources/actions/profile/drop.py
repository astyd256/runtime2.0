
import settings
import managers
import file_access

from ..auxiliary import show


def run():
    """
    drop last profile
    """

    location = settings.PROFILE_LOCATION

    if not managers.file_manager.exists(file_access.FILE, None, location):
        show("no profile")
        return

    show("drop profile")
    managers.file_manager.delete(file_access.FILE, None, location)
