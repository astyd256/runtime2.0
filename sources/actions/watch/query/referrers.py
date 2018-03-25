
from logs import console
from utils.structure import Structure
from utils.parsing import Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"query\"><option name=\"referrers\">%s</option></action>"
REQUEST_ALL = "<action name=\"query\"><option name=\"referrers\"/></action>"


def builder(parser):
    # <reply>
    def reply():
        result = Structure(referrers=None)
        # <referrers>
        def referrers():
            result.referrers = set()
            # <referrer>
            def referrer(id):
                result.referrers.add(id)
            # </referrer>
            return referrer
        # </referrers>
        yield referrers
        parser.accept(result)
    # </reply>
    return reply


def run(object, address=None, port=None, timeout=None, all=None):
    """
    query server
    :arg object: specifies origin object
    :param address: specifies server address
    :key int port: specifies server port
    :key float timeout: specifies timeout to wait for reply
    :key switch all: disable objects filtering
    """
    try:
        # request = REQUEST_ALL if all else REQUEST
        request = REQUEST % object
        message = query("query object referrers", address, port, request, timeout=timeout)
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
        with section("referrers"):
            for referrer in sorted(result.referrers):
                show(referrer)
