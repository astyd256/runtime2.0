
import gc
from collections import defaultdict

import managers
from utils.tracing import describe_object, describe_reference
from ..auxiliary import select_objects, get_type_name


SERVER_OPTION = "server"


def describe(options):
    gc.collect()

    if "changes" in options:
        source = managers.server.watcher.snapshot.recent
        if source is None:
            yield "<reply><error>No snapshot available</error></reply>"
            return
    elif "objects" in options:
        source = None
    elif "garbage" in options:
        source = gc.garbage
    else:
        return

    filter_by_server = options.get("filter") == SERVER_OPTION

    reference = defaultdict(list)
    for item in select_objects(server=filter_by_server, source=source):
        name = get_type_name(target_type=type(item))
        reference[name].append(item)

    yield "<reply>"
    yield "<descriptions>"
    for name, items in reference.iteritems():
        yield "<subgroup name=\"%s\">" % name.encode("xml")
        for item in items:
            yield "<description object=\"%s\">%s</description>" % (
                describe_object(item).encode("xml"), describe_reference(item).encode("xml"))
        yield "</subgroup>"
    yield "</descriptions>"
    yield "</reply>"
