
import os.path
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"query\"><option name=\"graph\">%s</option>%s</action>"

FILTER_OPTION = "<option name=\"filter\">%s</option>"
DEPTH_OPTION = "<option name=\"depth\">%s</option>"
MINIFY_OPTION = "<option name=\"minify\">0</option>"
CHANGES_OPTION = "<option name=\"source\">changes</option>"


def builder(parser):
    # <reply>
    def reply():
        result = Structure(graph=None)
        # <graph>
        def graph():
            result.graph = yield VALUE
        # </graph>
        yield graph
        parser.accept(result)
    # </reply>
    return reply


def generate_filename(object):
    return "%s.dot" % "-".join((part.lower() for part in object.split(".")))


def run(object, location=None, address=None, port=None, timeout=None, depth=None, filter=None, nominify=True, changes=False):
    """
    query object graph
    :param object: specifies origin object by its type name or identifier to make graph
    :param location: specifies location to store graph
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    :param int depth: specifies depth to scan
    :param str filter: specifies filter
    :param switch nominify: disable output minifying
    :param switch changes: use object changes as source
    """
    try:
        if location is None:
            location = generate_filename(object)
        elif os.path.isdir(location):
            location = os.path.join(location, generate_filename(object))
        elif not location.endswith(".dot"):
            location += ".dot"

        options = []
        if filter:
            options.append(FILTER_OPTION % filter)
        if depth:
            options.append(DEPTH_OPTION % depth)
        if not nominify:
            options.append(MINIFY_OPTION)
        if changes:
            options.append(CHANGES_OPTION)
        request = REQUEST % (object, "".join(options))

        message = query("query object graph", address, port, request, timeout=timeout)
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
            file.write(result.graph)
