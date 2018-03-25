
import os.path
import settings
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


ENDING = ".dot"

REQUEST = "<action name=\"query\"><option name=\"call-graph\"/>%s</action>"
REQUEST_SPECIFIC = "<action name=\"query\"><option name=\"call-graph\">%s</option>%s</action>"
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


def run(location, name=None, address=None, port=None, timeout=None, nodethreshold=None, edgethreshold=None):
    """
    query object graph
    :arg location: specifies location to store graph
    :param name: specifies profile name
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    :key float nodethreshold: specifies node threshold to filter
    :key float edgethreshold: specifies edge threshold to filter
    """
    try:
        if os.path.isdir(location):
            location = os.path.join(location, (name or settings.PROFILE_DEFAULT_NAME) + ENDING)
        elif not location.endswith(ENDING):
            location += ENDING

        options = []
        if nodethreshold:
            options.append(NODE_THRESHOLD_OPTION % nodethreshold)
        if edgethreshold:
            options.append(EDGE_THRESHOLD_OPTION % edgethreshold)

        request = REQUEST_SPECIFIC % (name, "".join(options)) if name else REQUEST % "".join(options)

        message = query("query call graph", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result or result.graph is None:
            raise Exception("Incorrect response")
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
    except Exception as error:
        console.error(error)
    else:
        console.write()

        if not result.graph:
            show("graph is empty")
            return

        with section("summary"):
            show("location", location)
            show("size", len(result.graph))

        with open(location, "wb") as file:
            file.write(result.graph.encode("utf8"))
