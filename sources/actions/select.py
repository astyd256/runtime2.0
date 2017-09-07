
import managers
from .auxiliary import section, show, warn, search


def update(data, identifier):
    if identifier:
        data[0] = str(identifier)
    elif 0 in data:
        del data[0]


def obtain(data):
    try:
        identifier = data[0]
    except KeyError:
        return "no"
    else:
        try:
            application = managers.memory.applications[identifier]
        except:
            return "%s" % identifier
        else:
            return "%s:%s" % (application.id, application.name.lower())


def select(application):
    with section("select %s as default application" % application, lazy=False):
        try:
            data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
            update(data, application.id if application else None)
            managers.storage.write_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"], data)
        except Exception as error:
            warn("unable to select application: %s" % error)


def retrieve():
        try:
            data = managers.storage.read_object(VDOM_CONFIG["VIRTUAL-HOSTING-STORAGE-RECORD"]) or {}
            return obtain(data)
        except Exception as error:
            warn("unable to retrieve default application: %s" % error)


def run(identifier=None):
    """
    select default application
    :param uuid_or_name identifier: application uuid or name
    """
    if identifier is None:
        identifier = retrieve()
        show("default application is %s" % identifier)
    else:
        entity, application = search(application=identifier)
        if application is None:
            warn("unable to find: %s" % identifier)
        else:
            select(application)
