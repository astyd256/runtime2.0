
import types
import numbers
import os
import gc
import resource
from utils.threads import SmartThread, SmartDaemon
from utils.tracing import clarify_source_path, get_threads_trace
from ..auxiliary import search_thread, search_object, get_type_name, get_thread_traceback, OptionError


def state(options):
    if "thread" in options:
        try:
            thread = search_thread(options["thread"])
            if thread is None:
                raise OptionError("Unable to find thread")
        except OptionError as error:
            yield "<reply><error>%s</error></reply>" % error
        else:
            trace_back = get_thread_traceback(thread)
            yield "<reply>"
            yield "<threads>"
            yield "<thread name=\"%s\" id=\"%d\" daemon=\"%s\" smart=\"%s\">" % \
                (thread.name.encode("xml"), thread.ident,
                    "yes" if thread.daemon else "no",
                    "yes" if isinstance(thread, (SmartThread, SmartDaemon)) else "no")
            yield "<stack>"
            for path, line, name, statement in trace_back:
                yield "<frame name=\"%s\" path=\"%s\" line=\"%d\"/>" % \
                    (name.encode("xml"), clarify_source_path(path).encode("xml"), line)
            yield "</stack>"
            yield "</thread>"
            yield "</threads>"
            yield "</reply>"
    elif "object" in options:
        try:
            object = search_object(options["object"])
            if object is None:
                raise OptionError("Unable to find object")
        except OptionError as error:
            yield "<reply><error>%s</error></reply>" % error
        else:
            yield "<reply>"
            yield "<objects>"
            yield "<object id=\"%08X\" type=\"%s\">" % (id(object), get_type_name(object))
            yield "<attributes>"
            for name in dir(object):
                try:
                    value = getattr(object, name)
                    yield "<attribute name=\"%s\">" % name
                    if value is None:
                        yield "<object id=\"%08X\" type=\"%s\"/>" % (id(value), get_type_name(value))
                    elif isinstance(value, (basestring, numbers.Number, bool)):
                        yield "<object id=\"%08X\" type=\"%s\">%r</object>" % (id(value), get_type_name(value), value)
                    else:
                        yield "<object id=\"%08X\" type=\"%s\"/>" % (id(value), get_type_name(value))
                    yield "</attribute>"
                except:
                    yield "<attribute name=\"%s\"/>"
            yield "</attributes>"
            yield "</object>"
            yield "</objects>"
            yield "</reply>"
    else:
        yield "<reply>"
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
        except:
            yield "<process id=\"%d\"/>" % os.getpid()
        else:
            yield "<process id=\"%d\">" % os.getpid()
            yield "<usage utime=\"%.3f\" stime=\"%.3f\" maxrss=\"%d\" idrss=\"%d\" ixrss=\"%d\"/>" % \
                (usage.ru_utime, usage.ru_stime, usage.ru_maxrss, usage.ru_idrss, usage.ru_ixrss)
            yield "</process>"
        yield "<threads>"
        for thread, stack in get_threads_trace():
            yield "<thread id=\"%d\" name=\"%s\"%s%s/>" % \
                (thread.ident, thread.name.encode("xml"),
                "" if thread.is_alive() else " alive=\"no\"",
                "" if isinstance(thread, SmartThread) else " smart=\"no\""
                " daemon=\"yes\"" if thread.daemon else "")
        yield "</threads>"
        yield "<garbage-collector>"
        yield "<objects>%d</objects>" % len(gc.get_objects())
        yield "<garbage>%d</garbage>" % len(gc.garbage)
        yield "<collection>"
        for count in gc.get_count():
            yield "<generation>%d</generation>" % count
        yield "</collection>"
        yield "</garbage-collector>"
        yield "</reply>"
