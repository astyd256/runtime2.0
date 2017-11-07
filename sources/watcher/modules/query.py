
import sys
import gc

from logs import log
from utils.profiling import profiler
from ..auxiliary import select_types, select_objects, \
    generate_graph, generate_call_graph_profile, generate_call_graph


SERVER_ONLY = "server only"
MISSING = "MISSING"


def query(options):
    gc.collect()

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

    elif "profile" in options:
        name = options["profile"]

        specific_profiler = profiler(name) if name else profiler
        data = specific_profiler.load()

        yield "<reply>"
        if data is None:
            yield "<profile/>"
        else:
            yield "<profile>"
            yield data.encode("base64").encode("cdata")
            yield "</profile>"
        yield "</reply>"

    elif "call-graph" in options:
        name = options["call-graph"]
        node_threshold = options.get("node-threshold")
        edge_threshold = options.get("edge-threshold")
        color_nodes = options.get("color-nodes")

        specific_profiler = profiler(name) if name else profiler
        keywords = {}

        if node_threshold:
            try:
                keywords["node_threshold"] = float(node_threshold)
            except ValueError:
                log.warning("Ignore wrond node threshold: %s" % node_threshold)

        if edge_threshold:
            try:
                keywords["edge_threshold"] = float(edge_threshold)
            except ValueError:
                log.warning("Ignore wrond edge threshold: %s" % edge_threshold)

        if color_nodes:
            try:
                keywords["color_nodes"] = bool(color_nodes)
            except ValueError:
                log.warning("Ignore wrond color nodes: %s" % color_nodes)

        with specific_profiler.hold() as location:
            profile = generate_call_graph_profile(location)
        data = generate_call_graph(profile, **keywords) if profile else None

        yield "<reply>"
        if data is None:
            yield "<call-graph/>"
        else:
            yield "<call-graph>"
            yield data.encode("xml")
            yield "</call-graph>"
        yield "</reply>"
