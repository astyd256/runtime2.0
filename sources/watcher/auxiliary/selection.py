
import gc
import threading

from utils.tracing import is_server_object
from .auxiliary import get_type_name


def search_thread(string):
    if not string:
        return None
    elif string[0] in "-0123456789":
        number = int(string)
        for thread in threading.enumerate():
            if thread.ident == number:
                return thread
        return None
    else:
        string = string.lower()
        for thread in threading.enumerate():
            if thread.name.lower() == string:
                return thread
        return None


def select_threads(string):
    if not string:
        return threading.enumerate()
    elif string[0] in "-0123456789":
        number = int(string)
        return tuple(thread for thread in threading.enumerate() if thread.ident == number)
    else:
        return tuple(thread for thread in threading.enumerate() if thread.name == string)


def search_object(string):
    if not string:
        return None
    elif string[0].upper() in "0123456789ABCDEF":
        number = int(string, 16)
        for object in gc.get_objects():
            if id(object) == number:
                return object
        return None
    else:
        for object in gc.get_objects():
            if get_type_name(object) == string:
                return object
        return None


def select_objects(string=None, server=True, unknown=True, source=None, filter=None):
    if source is None:
        source = gc.get_objects()

    if not string:
        objects = (object for object in source)
    elif string.isdigit():
        identifier = int(string, 16)
        objects = (object for object in source if id(object) == identifier)
    else:
        objects = (object for object in source if get_type_name(object) == string)

    if server:
        objects = (object for object in source if is_server_object(object, default=unknown))

    if filter:
        objects = (object for object in source if filter(object))

    return tuple(objects)


def select_types(server=True, unknown=True):
    types = set()
    for object in gc.get_objects():
        if server and not is_server_object(object, default=unknown):
            continue
        types.add(get_type_name(object))
    return tuple(types)
