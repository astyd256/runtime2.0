
from contextlib import contextmanager
import managers
from utils.properties import roproperty
from .compiler import compile_declarations_n_libraries, compile_registations


ATTRIBUTE_NAME = "e2vdom_context"


class Context(object):

    def __init__(self, dynamic):
        self._dynamic = dynamic
        self._types = set()
        self._registrations = []

    dynamic = roproperty("_dynamic")
    types = roproperty("_types")
    registrations = roproperty("_registrations")


def process(container, parent=None):
    try:
        context = getattr(managers.request_manager.current, ATTRIBUTE_NAME)
    except AttributeError:
        context = Context(dynamic=False)
        setattr(managers.request_manager.current, ATTRIBUTE_NAME, context)

    parent = container._parent.id if container._parent else None
    registrations = compile_registations(container, parent, dynamic=context.dynamic)
    context.registrations.append(registrations)


def generate(container):
    try:
        context = getattr(managers.request_manager.current, ATTRIBUTE_NAME)
    except AttributeError:
        context = Context(dynamic=False)
        setattr(managers.request_manager.current, ATTRIBUTE_NAME, context)

    types = container._types
    render_type = container._origin.type.render_type
    render_container = container._origin.container.type.id  # container._origin.type.id

    return compile_declarations_n_libraries(types,
        render_type, render_container, context.registrations, dynamic=context.dynamic)


@contextmanager
def select(dynamic=False):
    previous = getattr(managers.request_manager.current, ATTRIBUTE_NAME, None)
    context = Context(dynamic=dynamic)
    setattr(managers.request_manager.current, ATTRIBUTE_NAME, context)
    try:
        yield
    finally:
        if previous:
            setattr(managers.request_manager.current, ATTRIBUTE_NAME, previous)
        else:
            delattr(managers.request_manager.current, ATTRIBUTE_NAME)
