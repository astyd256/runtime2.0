
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"analyze\"><option name=\"garbage\">server only</option></action>"
REQUEST_ALL = "<action name=\"analyze\"><option name=\"garbage\"/></action>"

SORT_BY_NAME = "SORT BY NAME"
SORT_BY_COUNTER = "SORT BY COUNTYER"
SORT_VALUES = {
    "name": SORT_BY_NAME,
    "counter": SORT_BY_COUNTER
}

ORDER_BY_ASCENDING = "ORDER BY ASCENDING"
ORDER_BY_DESCENDING = "ORDER BY DESCENDING"
ORDER_VALUES = {
    "asc": ORDER_BY_ASCENDING,
    "desc": ORDER_BY_DESCENDING
}


def sort_by_name(x):
    return x[0]


def sort_by_counter(x):
    return x[1]


def builder(parser):
    # <reply>
    def reply():
        result = Structure(counters=None)
        # <counters>
        def counters():
            result.counters = []
            # <counter>
            def counter(object):
                counter = yield VALUE
                result.counters.append((object, int(counter)))
            # </counter>
            return counter
        # </counters>
        yield counters
        parser.accept(result)
    # </reply>
    return reply


def run(address=None, port=None, timeout=None, all=False, sort=None, order=None):
    """
    analyze server garbage
    :param address: specifies server address
    :param int port: specifies server port
    :param float timeout: specifies timeout to wait for reply
    :param switch all: disable objects filtering
    :param sort: sort entries by "name" or by "counter"
    :param order: sort entries "asc"ending or "desc"ending
    """
    try:
        sort = SORT_VALUES.get((sort or "").lower(), SORT_BY_NAME)
        if sort is SORT_BY_COUNTER and order is None:
            order = "desc"
        order = ORDER_VALUES.get((order or "").lower(), ORDER_BY_ASCENDING)
        request = REQUEST_ALL if all else REQUEST

        message = query("analyze objects", address, port, request, timeout=timeout)
        parser = Parser(builder=builder, notify=True, supress=True)
        result = parser.parse(message)
        if not result:
            raise Exception("Incorrect response")
    except ParsingException as error:
        console.error("unable to parse, line %s: %s" % (error.lineno, error))
    except Exception as error:
        console.error(error)
    else:
        console.write()
        with section("counters"):
            if result.counters:
                key = sort_by_counter if sort is SORT_BY_COUNTER else sort_by_name
                reverse = order is ORDER_BY_DESCENDING
                for name, counter in sorted(result.counters, key=key, reverse=reverse):
                    show(name, counter, longer=True)
            else:
                show("no objects")
