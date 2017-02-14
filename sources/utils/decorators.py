
def verificator(function):

    def check(value):
        try:
            function(value)
        except ValueError:
            return False
        else:
            return True

    function.check = check
    return function


def cache_by_argument(function):
    cache = {}

    def wrapper(key):
        try:
            return cache[key]
        except KeyError:
            return cache.setdefault(key, function(key))

    return wrapper
