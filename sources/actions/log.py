
from time import sleep
import managers
from logs import console


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
        console.error("unable to find log: %s" % name)
        return

    try:
        view = log.view()
        update = 25
        while True:
            entries = view.read(0, update, format=True)
            for entry in reversed(entries):
                console.write(entry)
            sleep(0.5)
            update = view.update()
    except Exception as error:
        console.error("unable to view log: %s" % error)
        raise
