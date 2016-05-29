
import gc
from collections import defaultdict
from ..auxiliary import select_objects, get_type_name


SERVER_ONLY = "server only"


def analyze(options):
    if "objects" in options:
        reference = defaultdict(int)
        for item in select_objects(server=options["objects"] == SERVER_ONLY):
            reference[type(item)] += 1
        yield "<reply>"
        yield "<counters>"
        for item, counter in reference.iteritems():
            name = get_type_name(target_type=item)
            yield "<counter object=\"%s\">%d</counter>" % (name.encode("xml"), counter)
        yield "</counters>"
        yield "</reply>"
    elif "garbage" in options:
        reference = defaultdict(int)
        for item in select_objects(server=options["garbage"] == SERVER_ONLY, source=gc.garbage):
            reference[type(item)] += 1
        yield "<reply>"
        yield "<counters>"
        for item, counter in reference.iteritems():
            name = item.__name__ if item.__module__ == "__builtin__" else "%s.%s" % (item.__module__, item.__name__)
            yield "<counter object=\"%s\">%d</counter>" % (name.encode("xml"), counter)
        yield "</counters>"
        yield "</reply>"
