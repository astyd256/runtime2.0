
import ctypes
import re
from utils.threads import SmartThread
from ..auxiliary import search_thread, search_object, get_type_name, get_thread_traceback, OptionError


pattern = re.compile("[A-Za-z][0-9A-Za-z]*$")


def intrude(options):
    if "raise" in options:
        try:
            value = options["raise"]
            if not pattern.match(value):
                raise ValueError
            exception = eval(value)
            if not issubclass(exception, Exception):
                raise ValueError
            thread = search_thread(options["thread"])
            if thread is None:
                raise OptionError("Unable to find thread")
        except OptionError as error:
            yield "<reply><error>%s</error></reply>" % error
        else:
            if ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(exception)) > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, 0)
                yield "<reply><error>Unable to raise</error></reply>" % error
            else:
                yield "<reply/>"
    elif "stop" in options:
        try:
            thread = search_thread(options["thread"])
            if thread is None:
                raise OptionError("Unable to find thread")
            if not isinstance(thread, SmartThread):
                raise OptionError("Thread is not smart")
        except OptionError as error:
            yield "<reply><error>%s</error></reply>" % error
        else:
            thread.stop()
            yield "<reply/>"
