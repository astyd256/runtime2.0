
from logs import console
from utils.structure import Structure
from utils.parsing import VALUE, Parser, ParsingException
from ...auxiliary import section, show
from ..auxiliary import query


REQUEST = "<action name=\"describe\"><option name=\"%s\"/>%s</action>"
FILTER_BY_SERVER_OPTION = "<option name=\"filter\">server</option>"

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
    return x[1], -x[2], x[0]


def builder(parser):
    # <reply>
    def reply():
        result = Structure(entries=None)
        # <descriptions>
        def descriptions():
            result.entries = []
            # <subgroup>
            def subgroup(name):
                subgroup = []
                result.entries.append((name, subgroup))
                # <description>
                def description(object):
                    value = yield VALUE
                    subgroup.append((object, value))
                # </description>
                return description
            # </subgroup>
            return subgroup
        # </descriptions>
        yield descriptions
        parser.accept(result)
    # </reply>
    return reply


def describe(subject, address, port, timeout, all, sort, order, limit):
    try:
        sort = SORT_VALUES.get((sort or "").lower(), SORT_BY_NAME)
        if sort is SORT_BY_COUNTER and order is None:
            order = "desc"
        order = ORDER_VALUES.get((order or "").lower(), ORDER_BY_ASCENDING)

        options = "".join(filter(None, (None if all else FILTER_BY_SERVER_OPTION,)))
        request = REQUEST % (subject, options)

        message = query("describe objects", address, port, request, timeout=timeout)
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
        with section("objects"):
            if result.entries:
                key = sort_by_counter if sort is SORT_BY_COUNTER else sort_by_name
                reverse = order is ORDER_BY_DESCENDING
                entries = sorted(result.entries, key=key, reverse=reverse)
                if limit is not None:
                    entries = entries[:limit]
                for name, subgroup in entries:
                    with section(name):
                        for object, description in subgroup:
                            with section(object, lazy=False):
                                for part in description.split(" < "):
                                    show(part, longer=True)
            else:
                show("no objects")
