
def lookup(object, path):
    names = path.split(".")

    if object.name != names[0]:
        return None

    result = object
    for name in names[1:]:
        result = result.objects.get(name)
        if not result:
            return None
    return result
