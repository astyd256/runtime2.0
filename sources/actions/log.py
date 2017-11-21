
from time import sleep
import managers
from .auxiliary import show, warn


PREVIOUS_LOG_LINES_TO_SHOW = 25
UPDATE_INTERVAL = 0.5


def run(name="server", uuid=None):
    """
    view log
    :param name: log name
    :param uuid uuid: application uuid
    """
    if name in ("server", "network", "security"):
        log = getattr(managers.log_manager.logs, name)
    elif name == "application":
        log = managers.log_manager.logs.application(uuid)
    else:
        warn("unable to find log: %s" % name)
        return

    try:
        view = log.view()
        update = PREVIOUS_LOG_LINES_TO_SHOW
        while 1:
            entries = view.read(0, update, format=True)
            for entry in reversed(entries):
                show(entry, noclip=True)
            sleep(UPDATE_INTERVAL)
            update = view.update()
    except Exception as error:
        warn("unable to view log: %s" % error)
        raise
