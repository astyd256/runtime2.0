
from contextlib import contextmanager
from utils.structure import Structure
import managers
from .compiler import compile_declarations_n_libraries, compile_registations


ATTRIBUTE_NAME = "e2vdom_context"


def initiate(static=True, dynamic=True):
    context = Structure(dynamic=False, dynamic_types=set(), registrations=[], dynamic_registrations=[])
    setattr(managers.request_manager.current, ATTRIBUTE_NAME, context)
    return context


def process(container, parent=None):
    context = getattr(managers.request_manager.current, ATTRIBUTE_NAME, None) or initiate()

    parent = container._parent.id if container._parent else None
    registrations = compile_registations(container, parent, dynamic=context.dynamic)
    (context.dynamic_registrations if context.dynamic else context.registrations).append(registrations)


def generate(container):
    context = getattr(managers.request_manager.current, ATTRIBUTE_NAME, None) or initiate()

    types = container._types
    render_type = container._origin.type.render_type
    render_container = container._origin.type.id

    declarations, libraties = \
        compile_declarations_n_libraries(types, render_type, render_container, context.registrations)
    dynamic_declarations, dynamic_libraties = \
        compile_declarations_n_libraries(context.dynamic_types - types, render_type, render_container, context.dynamic_registrations, dynamic=True)

    return (declarations, libraties), (dynamic_declarations, dynamic_libraties)


@contextmanager
def select(dynamic):
    context = getattr(managers.request_manager.current, ATTRIBUTE_NAME, None) or initiate()

    previous, context.dynamic = context.dynamic, dynamic
    yield
    context.dynamic = previous


def update(types=None):
    context = getattr(managers.request_manager.current, ATTRIBUTE_NAME, None) or initiate()
    context.dynamic_types |= types
