
import sys
import traceback


def quote(string):
    return string.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\0", "\\\\0")


def get_type_name(target=None, target_type=None):
    if target_type is None:
        target_type = type(target)
    return target_type.__name__ if target_type.__module__ == "__builtin__" \
        else "%s.%s" % (target_type.__module__, target_type.__name__)


def get_thread_traceback(thread):
    return traceback.extract_stack(sys._current_frames()[thread.ident])
