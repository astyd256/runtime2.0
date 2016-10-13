
from utils.console import CONSOLE_WIDTH
from logs import console
from .auxiliary import section, show, search_object, search_action


INDENT = "    "
SELECTION = "- "


def describe(item, extra=False):
    if hasattr(item, "is_object"):
        entity = item.type.name if item.is_object else "application"
        if item.is_object and item.type.name == "copy":
            copy = item.application.objects.catalog.get(item.attributes["source_object"])
            if copy:
                copy = describe(copy)
        else:
            copy = None
    else:
        entity = "action"
        copy = None

    return " ".join(filter(None, (
        entity if extra else None,
        ":".join(filter(None, (item.id, item.name.lower()))),
        ("-> %s" % copy) if copy else None)))


def search_parents(item):
    items = []
    if not hasattr(item, "is_object"):
        item = item.owner
        items.append(item)
    if item.is_object:
        current = item.parent
        while current:
            items.append(current)
            current = current.parent
        items.append(item.application)
        items.reverse()
    return items


def show_level(item, level=0, expand=False, select=False, indent=""):
    indent = indent + INDENT * level
    if select and len(indent) >= len(SELECTION):
        indent = indent[:-len(SELECTION)] + SELECTION
    show("%s%s" % (indent, describe(item, extra=True)), longer=True)
    if expand and hasattr(item, "is_object"):
        for subitem in item.objects.itervalues():
            show_level(subitem, level + 1, expand=expand)
        for subitem in item.actions.itervalues():
            show_level(subitem, level + 1)


def run(identifier):
    """
    inspect object
    :param uuid identifier: object uuid to inspect
    """
    subject = search_object(identifier)
    if subject:
        entity = subject.type.name if subject.is_object else "application"
    else:
        subject = search_action(identifier)
        if subject:
            entity = "action"
        else:
            console.error("unable to find: %s" % identifier)
            return

    with section("summary"):
        show("type", entity)
        show("id", subject.id)
        show("name", subject.name)

    parents = search_parents(subject)
    with section("structure", width=CONSOLE_WIDTH):
        for level, item in enumerate(parents):
            show_level(item, level)
        show_level(subject, len(parents), expand=True, select=True)
