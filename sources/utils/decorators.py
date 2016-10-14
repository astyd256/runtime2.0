
def cache_by_argument(function):
    cache = {}

    def wrapper(key):
        try:
            return cache[key]
        except KeyError:
            return cache.setdefault(key, function(key))

    return wrapper
