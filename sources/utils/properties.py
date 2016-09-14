
from weakref import ref
from threading import RLock


WEAK_NAME_TEMPLATE = "_weak_%s"


def lazy(initializer):
    name = initializer.__name__
    lock = RLock()

    class LazyProperty(object):

        def __get__(self, instance, owner=None):
            with lock:
                try:
                    return instance.__dict__[name]
                except KeyError:
                    return instance.__dict__.setdefault(name, initializer(instance))

    return LazyProperty()


def _weak(name):

    class WeakProperty(object):

        def __get__(self, instance, owner=None):
            try:
                value = instance.__dict__[name]
            except KeyError:
                raise AttributeError(name)
            return None if value is None else value()

        def __set__(self, instance, value):
            instance.__dict__[name] = None if value is None else ref(value)

        def __delete__(self, instance):
            del instance.__dict__[name]

    return WeakProperty()


def weak(*names):

    def wrapper(cls):
        for name in names:
            setattr(cls, name, _weak(WEAK_NAME_TEMPLATE % name))
        return cls

    return wrapper


def constant(value):

    class ConstantProperty(object):

        def __get__(self, instance, owner=None):
            return value

        def __set__(self, instance, value):
            raise AttributeError

        def __delete__(self, instance):
            raise AttributeError

    return ConstantProperty()


def roproperty(name):
    namespace = {}
    bytecode = compile("""
class ReadOnlyProperty(object):

    __module__ = "utils"

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        if instance.{name} is not value:  # hack to allow in-place operators
            raise AttributeError("{name}")

    def __delete__(self, instance):
        raise AttributeError
        """.format(name=name), "<roproperty>", "exec")
    exec(bytecode, namespace)
    return namespace["ReadOnlyProperty"]()


def rwproperty(name, setter=None):
    if setter is None:
        namespace = {}
        assigment = "instance.%s = value" % name
    else:
        namespace = {"setter": setter}
        assigment = "setter(instance, value)"

    bytecode = compile("""
class ReadWriteProperty(object):

    __module__ = "utils"

    def __get__(self, instance, owner=None):
        return instance.{name}

    def __set__(self, instance, value):
        {assigment}

    def __delete__(self, instance):
        raise AttributeError
        """.format(name=name, assigment=assigment), "<rwproperty>", "exec")

    exec(bytecode, namespace)
    return namespace["ReadWriteProperty"]()
