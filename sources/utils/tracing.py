
import sys
import types
import linecache
import traceback
import inspect
import pprint
import threading
import os
from itertools import islice
import settings
from utils.auxiliary import headline, fit, align, lfill
from utils.console import width


LOGGING = None
TRACING = None

BINARY_ALIAS = "<sources>"
SERVER_ALIAS = "<server>"
TYPES_ALIAS = "<types>"
APPLICATIONS_ALIAS = "<applications>"
PYTHON_ALIAS = "<python>"

UNKNOWN_STATEMENT = "???"
COMPACT_DEFAULT_MODE = False
DEEPER_LATER = 1
DEFAULT_FILLER = "."

DESIRED_WIDTH = 139
CAPTION_WIDTH = 36
LOCATION_WIDTH = 99 if width == sys.maxint else min(width * 2 // 3, 99)
STATEMENT_WIDTH = DESIRED_WIDTH - LOCATION_WIDTH
NAME_WIDTH = 32
VALUE_WIDTH = DESIRED_WIDTH - NAME_WIDTH

BINARY_PATH = os.path.dirname(sys.argv[0]) or os.getcwd()
SERVER_PATH = os.path.split(BINARY_PATH)[0]
TYPES_PATH = os.path.abspath(os.path.join(BINARY_PATH, settings.TYPES_LOCATION))
APPLICATIONS_PATH = os.path.abspath(os.path.join(BINARY_PATH, settings.APPLICATIONS_LOCATION))
PYTHON_PATH = sys.prefix

WELL_KNOWN_MODULES = "_json", "_ast", "thread", "operator", "itertools", "exceptions"


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
    if path.startswith(BINARY_PATH):
        return BINARY_ALIAS + path[len(BINARY_PATH):]
    elif path.startswith(TYPES_PATH):
        return TYPES_ALIAS + path[len(TYPES_PATH):]
    elif path.startswith(APPLICATIONS_PATH):
        return APPLICATIONS_ALIAS + path[len(APPLICATIONS_PATH):]
    elif path.startswith(SERVER_PATH):
        return SERVER_ALIAS + path[len(SERVER_PATH):]
    elif path.startswith(PYTHON_PATH):
        return PYTHON_ALIAS + path[len(PYTHON_PATH):]
    else:
        return path


def restore_source_path(path):
    if path.startswith(BINARY_ALIAS):
        return BINARY_PATH + path[len(BINARY_ALIAS):]
    elif path.startswith(TYPES_ALIAS):
        return TYPES_PATH + path[len(TYPES_ALIAS):]
    elif path.startswith(APPLICATIONS_ALIAS):
        return APPLICATIONS_PATH + path[len(APPLICATIONS_ALIAS):]
    elif path.startswith(SERVER_ALIAS):
        return SERVER_PATH + path[len(SERVER_ALIAS):]
    elif path.startswith(PYTHON_ALIAS):
        return PYTHON_PATH + path[len(PYTHON_PATH):]
    else:
        return path


def extract_stack(frame=None, skip_tracing=True, skip=None, until=None):
    if frame is None:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            frame = sys.exc_info()[2].tb_frame.f_back

    lines = []
    while frame is not None:
        namespace = frame.f_globals
        lineno = frame.f_lineno
        code = frame.f_code
        filename = code.co_filename
        name = code.co_name

        if skip_tracing:
            if namespace.get("TRACING", KeyError) is None:
                frame = frame.f_back
                continue
            else:
                skip_tracing = False

        if until:
            module_name = namespace.get("__name__")
            if module_name and module_name.startswith(until):
                break

        if skip and name in skip:
            frame = frame.f_back
            continue
        else:
            skip = None

        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        if line:
            line = line.strip()
        else:
            line = None

        lines.append((filename, lineno, name, line))
        frame = frame.f_back

    lines.reverse()
    return lines


# detectors

def is_builtin_object(object):
    return type(object).__module__ == "__builtin__"


def is_server_object(object, default=True):
    module_name = type(object).__module__
    if module_name == "__builtin__":
        return False
    else:
        try:
            module_location = sys.modules[module_name].__file__
            if os.path.isabs(module_location):
                return module_location.startswith(BINARY_PATH)
        except:
            pass

        if module_name in WELL_KNOWN_MODULES:
            return False
        else:
            return default


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
    return "%s: %s" % (extype.__name__, headline(value)) if value else extype.__name__


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

def format_source_point(path, line, function, indent="", width=LOCATION_WIDTH):
    ending = fit(":%s:%s" % (line, function), NAME_WIDTH)
    fullname = fit(clarify_source_path(path), width - len(indent) - len(ending))
    return fullname + ending


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
            indent += settings.LOGGING_INDENT

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
        statements=True, caption=None, header=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, skip=None, until=None, into=None):
    lines = [] if into is None else into

    if thread is None:
        stack = extract_stack(skip=skip, until=until)
    else:
        try:
            frame = sys._current_frames()[thread.ident]
        except KeyError:
            return "" if into is None else None
        else:
            stack = extract_stack(frame, skip=skip, until=until)

    if caption:
        lines.append(caption)

    if header:
        if thread is None:
            thread = threading.current_thread()
        caption = describe_thread(thread)
    else:
        caption = None

    format_trace(stack,
        limit=limit,
        statements=statements,
        caption=caption,
        compact=compact,
        indent=indent,
        filler=filler,
        into=lines)

    if into is None:
        lines.append("")
        return "\n".join(lines)


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
            header=True,
            compact=compact,
            indent=indent,
            filler=filler,
            skip=None,
            until=None,
            into=lines)

    if into is None:
        lines.append("")
        return "\n".join(lines)


def format_exception_locals(information=None, ignore_builtins=True, caption=None,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    extype, exvalue, extraceback = information or sys.exc_info()
    frame = inspect.getinnerframes(extraceback)[-1][0]

    if caption:
        lines.append(indent + caption)
        indent += settings.LOGGING_INDENT

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
        statements=True, caption=None, label=None, compact=COMPACT_DEFAULT_MODE,
        locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, into=None):
    lines = [] if into is None else into
    extype, exvalue, extraceback = information = information or sys.exc_info()
    stack = traceback.extract_tb(extraceback)

    if separate:
        separator = lfill("- ", LOCATION_WIDTH + STATEMENT_WIDTH + (CAPTION_WIDTH if compact else 0))
        lines.append(separator)

    if caption:
        lines.append(caption)

    description = describe_exception(extype, exvalue)
    if label:
        description = "%s: %s" % (label, description)
    lines.append("%s%s" % (indent, description))

    if locals:
        format_exception_locals(information, indent=indent + settings.LOGGING_INDENT, into=lines)

    format_trace(stack,
        limit=limit,
        statements=statements,
        compact=compact,
        caption=describe_thread(threading.current_thread()),
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
        statements=True, caption=None, header=False, compact=COMPACT_DEFAULT_MODE,
        indent="", filler=DEFAULT_FILLER, skip=None, until=None, output=None):
    (output or sys.stdout).write(format_thread_trace(
        thread, limit, statements, caption, header, compact, indent, filler, skip, until))


def show_threads_trace(limit=sys.maxint,
        statements=True, compact=COMPACT_DEFAULT_MODE, current=True,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stdout).write(format_threads_trace(
        limit, statements, compact, current, indent, filler))


def show_exception_locals(information=None, ignore_builtins=True, caption=None,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_locals(
        information, ignore_builtins, caption, indent, filler))


def show_exception_trace(information=None, limit=sys.maxint,
        statements=True, caption=None, label=None, compact=COMPACT_DEFAULT_MODE,
        locals=False, threads=False, separate=False,
        indent="", filler=DEFAULT_FILLER, output=None):
    (output or sys.stderr).write(format_exception_trace(
        information, limit, statements, caption, label, compact,
        locals, threads, separate, indent, filler))
