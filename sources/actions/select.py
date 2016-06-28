
import managers
from .auxiliary import section, show


def update(data, application):
    if application:
        data[0] = str(application.id)
    elif 0 in data:
        del data[0]


def select(application):
    with section("select %s: %s as default application" % (application.id, application.name), instant=True):
        try:
            data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
            update(data, application)
            managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], data)
        except Exception as error:
            show("unable to select application: %s" % error)
            raise


def run(identifier):
    """
    select default application
    :param uuid_or_name identifier: application uuid or name
    """
    try:
        application = managers.memory.applications.search(identifier)
    except KeyError:
        show("unable to find application with such uuid or name")
        return

    select(application)
