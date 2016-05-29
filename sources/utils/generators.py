

ENSURE_NAME_ATTEMPTS = 1000000


def generate_unique_name(prefix, namespace):
    for index in xrange(1, ENSURE_NAME_ATTEMPTS):
        name = "%s%d" % (prefix, index)
        if name not in namespace:
            return name
    raise Exception(u"Unable to generate name")
