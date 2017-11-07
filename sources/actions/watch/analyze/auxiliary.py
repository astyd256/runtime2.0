
import re
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"analyze\"><option name=\"%s\"/>%s</action>"
FILTER_BY_SERVER_OPTION = "<option name=\"filter\">server</option>"
GROUP_BY_NAME_OPTION = "<option name=\"group\">name</option>"

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

COUNTER_REGEX = re.compile("(\d+)(?:\s*\((\d+)\))?")


def sort_by_name(x):
    return x[0]


def sort_by_counter(x):
    return x[1], -x[2], x[0]


def builder(parser):
    # <reply>
    def reply():
        result = Structure(counters=None)
        # <counters>
        def counters():
            result.counters = []
            # <counter>
            def counter(object):
                value = yield VALUE
                match = COUNTER_REGEX.match(value)
                if match:
                    counter, items = int(match.group(1)), int(match.group(2) or 0)
                    result.counters.append((object, counter, items, value))
                else:
                    result.counters.append((object, 0, 0, "error: " + value))
            # </counter>
            return counter
        # </counters>
        yield counters
        parser.accept(result)
    # </reply>
    return reply


def analyze(subject, address, port, timeout, all, nogroup, sort, order, limit):
    try:
        sort = SORT_VALUES.get((sort or "").lower(), SORT_BY_NAME)
        if sort is SORT_BY_COUNTER and order is None:
            order = "desc"
        order = ORDER_VALUES.get((order or "").lower(), ORDER_BY_ASCENDING)

        options = "".join(filter(None, (None if all else FILTER_BY_SERVER_OPTION,
            None if nogroup else GROUP_BY_NAME_OPTION)))
        request = REQUEST % (subject, options)

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
                entries = sorted(result.counters, key=key, reverse=reverse)
                if limit is not None:
                    entries = entries[:limit]
                for name, counter, items, value in entries:
                    show(name, value, longer=True)
            else:
                show("no objects")
