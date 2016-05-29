
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"query\"><option name=\"graph\">%s</option></action>"


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


def run(object, filename=None, address=None, port=None, timeout=None):
    """
    query object graph
    :param object: specifies origin object by its type name or identifier to make graph
    :param filename: specifies filename to store graph
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    """
    try:
        if filename is None:
            filename = "%s.dot" % "-".join((part.lower() for part in object.split(".")))

        message = query("query object graph", address, port, REQUEST % object, timeout=timeout)
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
            show("filename", filename)
            show("size", len(result.graph))

        with open(filename, "wb") as file:
            file.write(result.graph)
