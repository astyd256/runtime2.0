
from contextlib import contextmanager
from textwrap import wrap
from logs import console
from utils.structure import Structure
from utils.auxiliary import align


MISSING = "MISSING"
INDENT = "    "

LINE_WIDTH = 119
NAME_WIDTH = 36
LONG_NAME_WIDTH = 85


global_context = Structure(
    previous=None,
    show_section=None,
    indent="",
    width=LINE_WIDTH)


def escape(value):
    return "\"%s\"" % value.replace("\"", "\\\"")


@contextmanager
def section(name=None, value=MISSING, indent=None, longer=False, width=None, lazy=True):
    global global_context

    if indent is None:
        indent = global_context.indent

    def show_section():
        if context.previous and context.previous.show_section:
            context.previous.show_section()
        context.show_section = None
        show(name, value, indent, longer)

    context = Structure(
        previous=global_context,
        show_section=show_section,
        indent=indent + INDENT,
        width=width or LINE_WIDTH)

    if not (value is MISSING and lazy):
        context.show_section()

    global_context = context
    try:
        yield
    finally:
        global_context = context.previous


def show(name="", value=MISSING, indent=None, longer=False):
    global global_context

    if indent is None:
        indent = global_context.indent

    if global_context.show_section:
        global_context.show_section()

    if value is MISSING:
        caption = indent
        value = name
    else:
        if isinstance(longer, bool):
            width = LONG_NAME_WIDTH if longer else NAME_WIDTH
        else:
            width = longer
        caption = align(name, width, filler="." if name else " ", indent=indent)

    if not isinstance(value, basestring):
        value = str(value)

    message = "\n".join(("\n".join(wrap(
        part,
        initial_indent=caption,
        subsequent_indent=" " * len(caption),
        width=global_context.width,
        replace_whitespace=False,
        break_long_words=False))
        for part in value.splitlines()))
    console.write(message)


def confirm(message):
    console.write(message)
    console.stdout.write("are you sure? ")
    answer = raw_input()
    return answer.lower() == "yes"
