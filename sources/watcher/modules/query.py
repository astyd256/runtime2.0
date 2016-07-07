
import sys
import gc

from logs import log
from ..auxiliary import select_types, select_objects, generate_graph


SERVER_ONLY = "server only"
MISSING = "MISSING"


def query(options):
    if "types" in options:
        types = select_types(server=options["types"] == SERVER_ONLY)
        yield "<reply>"
        yield "<types>"
        for type in types:
            yield "<type id=\"%08X\" name=\"%s\"/>" % (id(type), type.encode("xml"))
        yield "</types>"
        yield "</reply>"

    elif "objects" in options:
        objects = select_objects(options["objects"])
        yield "<reply>"
        yield "<objects>"
        for object in objects:
            yield "<object id=\"%08X\"/>" % id(object)
        yield "</objects>"
        yield "</reply>"

    elif "garbage" in options:
        objects = gc.garbage
        yield "<reply>"
        yield "<objects>"
        for object in objects:
            yield "<object id=\"%08X\"/>" % id(object)
        yield "</objects>"
        yield "</reply>"

    elif "referrers" in options:
        objects = select_objects(options["referrers"])
        ignore = set((id(sys._getframe()), id(objects)))
        referrers = gc.get_referrers(*objects)
        yield "<reply>"
        yield "<referrers>"
        for referrer in referrers:
            if id(referrer) in ignore:
                continue
            yield "<referrer id=\"%08X\"/>" % id(referrer)
        yield "</referrers>"
        yield "</reply>"

    elif "referents" in options:
        objects = select_objects(options["referents"])
        ignore = set((id(sys._getframe()), id(objects)))
        referents = gc.get_referents(*objects)
        yield "<reply>"
        yield "<referents>"
        for referent in referents:
            if id(referent) in ignore:
                continue
            yield "<referent id=\"%08X\"/>" % id(referent)
        yield "</referents>"
        yield "</reply>"

    elif "graph" in options:
        filter = options.get("filter")
        depth = options.get("depth")
        minify = options.get("minify")

        if filter:
            try:
                filter_name, filter_value = filter.split("=")
                filter_value = eval(filter_value)

                def filter(object):
                    try:
                        return getattr(object, filter_name, MISSING) == filter_value
                    except:
                        return False
            except:
                log.warning("Ignore wrong filter: %s" % filter)
                filter = None

        objects = select_objects(options["graph"], server=False, filter=filter)
        keywords = {}

        if depth:
            try:
                keywords["depth"] = int(depth)
            except ValueError:
                log.warning("Ignore wrond depth: %s" % depth)

        if minify:
            minify = bool(int(minify))
            keywords["minify"] = minify
            keywords["skip_functions"] = minify

        yield "<reply>"
        yield "<graph>"
        yield "".join(generate_graph(objects, **keywords)).encode("xml")
        yield "</graph>"
        yield "</reply>"
