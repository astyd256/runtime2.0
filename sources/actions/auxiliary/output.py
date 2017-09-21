
from contextlib import contextmanager
from textwrap import wrap
from logs import console
from utils.structure import Structure
from utils.auxiliary import align
from utils.console import CONSOLE_WIDTH


ABSENT = "ABSENT"
INDENT = "    "
WARN_INDENT = ""

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
def section(name=None, value=ABSENT, indent=None, longer=False, width=None, lazy=True):
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

    if not (value is ABSENT and lazy):
        context.show_section()

    global_context = context
    try:
        yield
    finally:
        global_context = context.previous


def reformat(value, caption, noclip=False):
    global global_context
    return "\n".join(("\n".join(wrap(
        part,
        initial_indent=caption,
        subsequent_indent=" " * len(caption),
        width=CONSOLE_WIDTH if noclip else global_context.width,
        replace_whitespace=False,
        break_long_words=False))
        for part in value.splitlines()))


def show(name=None, value=ABSENT, indent=None, longer=False, noclip=False):
    global global_context

    if indent is None:
        indent = global_context.indent

    if global_context.show_section:
        global_context.show_section()

    if not name:
        if name is not None:
            console.write()
        return

    if value is ABSENT:
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

    console.write(reformat(value, caption, noclip=noclip))


def warn(message, indent=None, noclip=False):
    global global_context

    if indent is None:
        indent = WARN_INDENT

    if global_context.show_section:
        global_context.show_section()

    if not isinstance(message, basestring):
        message = str(message)

    console.error(reformat(message, indent, noclip=noclip))


def confirm(message=None, question=None):
    if message:
        console.write(message)
    console.stdout.write("are you sure%s? ___\b\b\b" % (" to %s" % question if question else ""))
    answer = raw_input()
    result = answer.lower() == "yes"
    if not result:
        console.write("unconfirmed")
    return result


def newline(lazy=True):
    global global_context

    def show_section():
        if context.previous and context.previous.show_section:
            context.previous.show_section()
        context.show_section = None
        show()

    context = Structure(
        previous=global_context,
        show_section=show_section,
        indent=global_context.indent,
        width=LINE_WIDTH)

    if not lazy:
        context.show_section()

    global_context = context
