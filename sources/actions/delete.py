
import managers
from .auxiliary import section, confirm, show, warn


def run(identifier="broken"):
    """
    delete (broken) application
    :param uuid identifier: application uuid
    """

    if not confirm("cleanup %s" % identifier):
        return

    with section():
        try:
            managers.memory.cleanup_application_infrastructure(identifier)
        except:  # noqa
            warn("unable to delete application")
            raise
        else:
            show("done")
