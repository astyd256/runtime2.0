
import managers
from logs import console


def run(uuid_or_name):
    """
    select default application
    :param uuid_or_name uuid_or_name: application uuid or name
    """

    try:
        application = managers.memory.applications.search(uuid_or_name)
        console.write("select %s: %s as default application" % (application.id, application.name))
    except KeyError:
        console.error("unable to find application with such uuid or name")
        return

    try:
        data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}

        if application:
            data[0] = str(application.id)
        elif 0 in data:
            del data[0]

        managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], data)
    except Exception as error:
        console.error("unable to select application: %s" % error)
        raise
