
import sys
import types
import traceback
import inspect
import pprint
import threading
import os
from itertools import islice
from utils.auxiliary import fit, align, lfill
from utils.console import width


PYTHON_ALIAS = "<python>"
SERVER_ALIAS = "<server>"

UNKNOWN_STATEMENT = "???"
COMPACT_DEFAULT_MODE = False
DEEPER_LATER = 1
DEFAULT_FILLER = "."

DESIRED_WIDTH = 139
CAPTION_WIDTH = 36
LOCATION_WIDTH = 79 if width == sys.maxint else min(width * 2 // 3, 79)
STATEMENT_WIDTH = DESIRED_WIDTH - LOCATION_WIDTH
NAME_WIDTH = 32
VALUE_WIDTH = DESIRED_WIDTH - NAME_WIDTH

BINARY_PATH = os.path.dirname(sys.argv[0]) or os.getcwd()
PYTHON_PATH = sys.prefix
SERVER_PATH = os.path.split(BINARY_PATH)[0]


# auxiliary

def iterlast(subject):
    if isinstance(subject, tuple):
        for last in subject:
            yield last
    else:
        last = subject
    while True:
        yield last


def clarify_source_path(path):
    if path.startswith("<"):
        return path
    path = os.path.normpath(path if os.path.isabs(path) else os.path.join(BINARY_PATH, path))
    if path.startswith(SERVER_PATH):
        return SERVER_ALIAS + path[len(SERVER_PATH):]
    elif path.startswith(PYTHON_PATH):
        return PYTHON_ALIAS + path[len(PYTHON_PATH):]
    else:
        return path


def restore_source_path(path):
    if path.startswith(SERVER_ALIAS):
        return SERVER_PATH + path[len(SERVER_ALIAS):]
    elif path.startswith(PYTHON_ALIAS):
        return PYTHON_PATH + path[len(PYTHON_PATH):]
    else:
        return path


# detectors

def is_builtin_object(object):
    return type(object).__module__ == "__builtin__"


def is_server_object(object, unknown=False):
    module_name = type(object).__module__
    if module_name == "__builtin__":
        return False
    try:
        return sys.modules[module_name].__file__.startswith(BINARY_PATH)
    except:
        return unknown


# describers

def describe_exception(extype, exvalue):
    try:
        if isinstance(exvalue, types.InstanceType):
            value = getattr(exvalue, "__str__")()
        else:
            try:
                value = str(exvalue)
            except:
                value = unicode(exvalue).encode("ascii", "backslashreplace")
    except Exception:
        value = ""
    return "%s: %s" % (extype.__name__, value) if value else extype.__name__


def describe_thread(thread):
    extra = tuple(filter(None, (
        "Daemon" if thread.daemon else None,
        "Stopping" if getattr(thread, "_stopping", None) else None)))
    if extra:
        return "%s (%d: %s)" % (thread.name, thread.ident, ", ".join(extra))
        # return "%s (%s)"%(thread.name, ", ".join(extra))
    else:
        return "%s (%d)" % (thread.name, thread.ident)
        # return thread.name


# formatting

def format_trace(stack, limit=sys.maxint,
        statements=True, caption=None, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    width = LOCATION_WIDTH
    entries = islice(reversed(stack), limit) if DEEPER_LATER else stack[len(stack) - limit:]

    if caption:
        if compact:
            indent = indent + align(caption, CAPTION_WIDTH, " ", "." if limit > 1 else " ")
            indent = indent, " " * len(indent)
            filler = ".", filler
            width += CAPTION_WIDTH
        else:
            lines.append(indent + caption)
            indent = indent + "    "

    indents, fillers = iterlast(indent), iterlast(filler)
    for path, line, function, statement in entries:
        indent, filler = indents.next(), fillers.next()
        ending = fit(":%s:%s" % (line, function), NAME_WIDTH)
        fullname = fit(clarify_source_path(path), width - len(indent) - len(ending))
        location = fullname + ending
        if statements:
            lines.append("%s%s%s" % (indent,
                align(location, width - len(indent), " ", filler=filler),
                align(statement or UNKNOWN_STATEMENT, STATEMENT_WIDTH, " ", filler=" ")))
        else:
            lines.append("%s%s" % (indent, location))

    if into is None:
        lines.append("")
        return "\n".join(lines)


def format_thread_trace(thread=None, limit=sys.maxint,
        statements=True, caption=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, into=None):
    if thread is None:
        stack = traceback.extract_stack()
    else:
        frame = sys._current_frames()[thread.ident]
        stack = traceback.extract_stack(frame)

    if caption:
        if thread is None:
            thread = threading.current_thread()
        caption = describe_thread(thread)

    return format_trace(stack,
        limit=limit,
        statements=statements,
        caption=caption,
        compact=compact,
        indent=indent,
        filler=filler,
        into=into)


def format_threads_trace(limit=sys.maxint,
        statements=True, compact=COMPACT_DEFAULT_MODE, current=True,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    current_thread = None if current else threading.current_thread()

    for thread in threading.enumerate():
        if thread == current_thread:
            continue
        format_thread_trace(thread,
            limit=limit,
            statements=statements,
            caption=True,
            compact=compact,
            indent=indent,
            filler=filler,
            into=lines)

    if into is None:
        lines.append("")
        return "\n".join(lines)


def format_exception_locals(information=None, ignore_builtins=True, indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    extype, exvalue, extraceback = information or sys.exc_info()
    frame = inspect.getinnerframes(extraceback)[-1][0]

    for name, value in frame.f_locals.iteritems():
        caption = align(name, NAME_WIDTH - len(indent), " ", filler=filler)
        if ignore_builtins and name == "__builtins__":
            lines.append("%s%s%s" % (indent, caption, "{...}"))
        else:
            lines.append("%s%s%s" % (indent, caption,
                pprint.pformat(value, width=VALUE_WIDTH).replace("\n", "\n%s%s" % ("", NAME_WIDTH * " "))))

    if into is None:
        lines.append("")
        return "\n".join(lines)


def format_exception_trace(information=None, limit=sys.maxint,
        statements=True, compact=COMPACT_DEFAULT_MODE, locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    extype, exvalue, extraceback = information = information or sys.exc_info()
    stack = traceback.extract_tb(extraceback)
    thread = threading.current_thread()

    if separate:
        separator = lfill("- ", LOCATION_WIDTH + STATEMENT_WIDTH + (CAPTION_WIDTH if compact else 0))
        lines.append(separator)

    lines.append("%s%s" % (indent, describe_exception(extype, exvalue)))

    if locals:
        format_exception_locals(information, indent="    ", into=lines)

    format_trace(stack,
        limit=limit,
        statements=statements,
        caption=describe_thread(thread),
        compact=compact,
        indent=indent,
        filler=filler,
        into=lines)

    if threads:
        format_threads_trace(
            limit=limit,
            statements=statements,
            compact=compact,
            current=False,
            indent=indent,
            filler=filler,
            into=lines)

    if separate:
        lines.append(separator)

    if into is None:
        lines.append("")
        return "\n".join(lines)


# auxiliary

def enumerate_thread_trace(thread=None):
    if thread is None:
        stack = traceback.extract_stack()
    else:
        frame = sys._current_frames()[thread if isinstance(thread, int) else thread.ident]
        stack = traceback.extract_stack(frame)
    for path, line, function, statement in stack:
        yield clarify_source_path(path), line, function, statement


def get_thread_trace(thread=None):
    return tuple(enumerate_thread_trace(thread))


def enumerate_threads_trace():
    for thread in threading.enumerate():
        yield thread, enumerate_thread_trace(thread)


def get_threads_trace():
    return tuple((thread, tuple(trace)) for thread, trace in enumerate_threads_trace())


# wrappers

def show_trace(stack, limit=sys.maxint,
        statements=True, caption=None, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_trace(
        stack, limit, statements, caption, compact, indent, filler))


def show_thread_trace(thread=None, limit=sys.maxint,
        statements=True, caption=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_thread_trace(
        thread, limit, statements, caption, compact, indent, filler))


def show_threads_trace(limit=sys.maxint,
        statements=True, compact=COMPACT_DEFAULT_MODE, current=True,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_threads_trace(
        limit, statements, compact, current, indent, filler))


def show_exception_locals(information=None,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_locals(
        information, indent, filler))


def show_exception_trace(information=None, limit=sys.maxint,
        statements=True, compact=COMPACT_DEFAULT_MODE, locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_trace(
        information, limit, statements, compact, locals, threads, separate, indent, filler))
