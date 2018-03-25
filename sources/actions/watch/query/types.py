
from logs import console
from utils.structure import Structure
from utils.parsing import Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"query\"><option name=\"types\">server only</option></action>"
REQUEST_ALL = "<action name=\"query\"><option name=\"types\"/></action>"


def builder(parser):
    # <reply>
    def reply():
        result = Structure(types=None)
        # <types>
        def types():
            result.types = []
            # <type>
            def type(id, name):
                result.types.append((id, name))
            # </type>
            return type
        # </types>
        yield types
        parser.accept(result)
    # </reply>
    return reply


def run(address=None, port=None, timeout=None, all=None):
    """
    query server
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    :key switch all: disable objects filtering
    """
    try:
        request = REQUEST_ALL if all else REQUEST
        message = query("query object graph", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result:
            console.error(message)
            raise Exception("Incorrect response")
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
        raise
    except Exception as error:
        console.error(error)
        raise
    else:
        console.write()
        with section("types"):
            for name in sorted(name for id, name in result.types):
                show(name)
