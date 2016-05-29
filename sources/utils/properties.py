
def lazy(initializer):
    namespace = {}
    exec("""
class LazyProperty(object):

    def __get__(self, instance, owner=None):
        instance.{name} = value = self._initializer(instance)
        return value
        """.format(name=initializer.__name__), namespace)
    instance = namespace["LazyProperty"]()
    instance._initializer = initializer
    return instance


def constant(value):
    namespace = {}
    exec("""
class ConstProperty(object):

    def __get__(self, instance, owner=None):
        return {value}

    def __set__(self, instance, value):
        raise AttributeError

    def __delete__(self, instance):
        raise AttributeError
        """.format(value=repr(value)), namespace)
    return namespace["ConstProperty"]()


def roproperty(name):
    namespace = {}
    exec("""
class ReadOnlyProperty(object):

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        if instance.{name} is not value:  # hack to allow in-place operators
            raise AttributeError("{name}")

    def __delete__(self, instance):
        raise AttributeError
        """.format(name=name), namespace)
    return namespace["ReadOnlyProperty"]()


def rwproperty(name, setter=None, notify=None):
    namespace = {}

    if notify is None:
        notify = ""
    else:
        if notify[-1] == ")":
            notify = "instance.%s" % notify
        else:
            notify = "instance.%s()" % notify

    if setter:
        exec("""
class ReadWriteProperty(object):

    def __init__(self, setter):
        self._setter = setter

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        self._setter(instance, value);{notify}

    def __delete__(self, instance):
        raise AttributeError
            """.format(name=name, notify=notify), namespace)
        return namespace["ReadWriteProperty"](setter)
    else:
        exec("""
class ReadWriteProperty(object):

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        instance.{name} = value;{notify}

    def __delete__(self, instance):
        raise AttributeError("{name}")
            """.format(name=name, notify=notify), namespace)
        return namespace["ReadWriteProperty"]()
