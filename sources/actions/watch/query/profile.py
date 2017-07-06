
import os.path
import settings

from logs import console
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


ENDING = "." + settings.PROFILE_EXTENSION

REQUEST = "<action name=\"query\"><option name=\"profile\"/></action>"
REQUEST_SPECIFIC = "<action name=\"query\"><option name=\"profile\">%s</option></action>"


def builder(parser):
    # <reply>
    def reply():
        # <graph>
        def profile():
            value = yield VALUE
            if value:
                parser.accept(value.decode("base64"))
        # </graph>
        yield profile
    # </reply>
    return reply


def run(location, name=None, address=None, port=None, timeout=None):
    """
    query profile statistics
    :param location: specifies location to store graph
    :param name: specifies profile name
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    """
    try:
        if os.path.isdir(location):
            location = os.path.join(location, (name or settings.PROFILE_DEFAULT_NAME) + ENDING)
        elif not location.endswith(ENDING):
            location += ENDING

        request = REQUEST_SPECIFIC % name if name else REQUEST

        message = query("query profile statistics", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
    else:
        console.write()
        if result:
            with section("summary"):
                show("location", location)
                show("size", len(result))
            with open(location, "wb") as file:
                file.write(result)
        else:
            show("no profile statistics")
