
import os.path
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


DEFAULT_FILENAME = "callgraph.dot"
REQUEST = "<action name=\"query\"><option name=\"call-graph\"/>%s</action>"
NODE_THRESHOLD_OPTION = "<option name=\"node-threshold\">%s</option>"
EDGE_THRESHOLD_OPTION = "<option name=\"edge-threshold\">%s</option>"


def builder(parser):
    # <reply>
    def reply():
        result = Structure(graph=None)
        # <graph>
        def call_graph():
            result.graph = yield VALUE
        # </graph>
        yield call_graph
        parser.accept(result)
    # </reply>
    return reply


def generate_filename(object):
    return "%s.dot" % "-".join((part.lower() for part in object.split(".")))


def run(location=None, address=None, port=None, timeout=None, nodethreshold=None, edgethreshold=None):
    """
    query object graph
    :param object: specifies origin object by its type name or identifier to make graph
    :param location: specifies location to store graph
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    :param float nodethreshold: specifies node threshold to filter
    :param float edgethreshold: specifies edge threshold to filter
    """
    try:
        if location is None:
            location = DEFAULT_FILENAME
        elif os.path.isdir(location):
            location = os.path.join(location, DEFAULT_FILENAME)
        elif not location.endswith(".dot"):
            location += ".dot"

        options = []
        if nodethreshold:
            options.append(NODE_THRESHOLD_OPTION % nodethreshold)
        if edgethreshold:
            options.append(EDGE_THRESHOLD_OPTION % edgethreshold)
        request = REQUEST % "".join(options)

        message = query("query call graph", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result or not result.graph:
            raise Exception("Incorrect response")
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
    except Exception as error:
        console.error(error)
    else:
        console.write()

        with section("summary"):
            show("location", location)
            show("size", len(result.graph))

        with open(location, "wb") as file:
            file.write(result.graph.encode("utf8"))
