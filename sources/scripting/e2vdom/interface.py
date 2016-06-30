
from threading import current_thread
from contextlib import contextmanager
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
    thread = current_thread()
    try:
        context = getattr(thread, ATTRIBUTE_NAME)
    except AttributeError:
        context = Context(dynamic=False)
        setattr(thread, ATTRIBUTE_NAME, context)

    parent = container._parent.id if container._parent else None
    registrations = compile_registations(container, parent, dynamic=context.dynamic)
    context.registrations.append(registrations)


def generate(container):
    thread = current_thread()
    try:
        context = getattr(thread, ATTRIBUTE_NAME)
    except AttributeError:
        context = Context(dynamic=False)
        setattr(thread, ATTRIBUTE_NAME, context)

    types = container._types
    render_type = container._origin.type.render_type
    render_container = container._origin.container.type.id  # container._origin.type.id

    return compile_declarations_n_libraries(types,
        render_type, render_container, context.registrations, dynamic=context.dynamic)


@contextmanager
def select(dynamic=False):
    thread = current_thread()
    previous = getattr(thread, ATTRIBUTE_NAME, None)

    context = Context(dynamic=dynamic)
    setattr(thread, ATTRIBUTE_NAME, context)

    try:
        yield
    finally:
        if previous:
            setattr(thread, ATTRIBUTE_NAME, previous)
        else:
            delattr(thread, ATTRIBUTE_NAME)
