
import re
from itertools import izip_longest
import managers
from logs import console
from .auxiliary import section, show


TYPE = "type"
APPLICATION = "application"

COLORS = {
    1: "gray",
    2: "green",
    3: "red",
    4: "blue"
}
EXPLANATIONS = {
    "dynamic": {0: "no", 1: "yes"},
    "moveable": {0: "no", 1: "yes"},
    "resizable": {0: "no", 1: "vertically", 2: "horizontally", 3: "yes"},
    "interface_type": {
        1: "standard",
        2: "richtext editor",
        3: "text editor",
        4: "picture",
        5: "special table",
        6: "no WYSIWYG presentation"
    },
    "container": {1: "non-container", 2: "container", 3: "top level container"}
}
NAME_WIDTH = 36
DESCRIPTION_WIDTH = 79


name_regex = re.compile(r"^([0-9A-Z]+)\((.+)\)", re.IGNORECASE)
dropdown_regex = re.compile(r"\|([^(|)]+)?\)")
lang_regex = re.compile(r"^#lang\((\d+)\)$", re.IGNORECASE)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def unlang(subject, value):
    try:
        match = lang_regex.search(value)
        return subject.sentences["en_US"][int(match.group(1))]
    except:
        return value


def explain(name, value):
    if name == "password":
        return "<present>" if value else "<absent>"
    elif name == "category":
        return value.lower() or "<empty>"

    try:
        explanations = EXPLANATIONS[name]
    except KeyError:
        return None

    try:
        explanation = explanations[int(value)]
    except ValueError:
        return "%r (not a number)" % value
    except KeyError:
        return "%r (unknown)" % value
    else:
        return "%s (%s)" % (value, explanation)


def interface(subject, attribute):

    def dropdown(value):
        def pair(description, value):
            if description:
                return "%s: %s" % (value, unlang(subject, description))
            else:
                return value
        try:
            pairs = (pair(left[1:], right[:-1]) for left, right in grouper(value.split("|"), 2))
            return "dropdown (%s)" % "; ".join(pairs)
        except:
            return "dropdown (...)"

    value = attribute.code_interface
    match = name_regex.search(value)
    if match:
        name = match.group(1).lower()
        if name == "dropdown":
            return dropdown(match.group(2))
        else:
            return name
    else:
        return value


def describe(subject, attribute):
    return unlang(subject, attribute.description).replace("\n", " ")


def run(uuid_or_name, description=False):
    """
    show application or type
    :param uuid_or_name uuid_or_name: application or type uuid or name
    :param switch description: show attributes description
    """

    subject = managers.memory.types.search(uuid_or_name)
    if subject:
        entity = TYPE
        names = ("id", "module_name", "name", "class_name",
            "category", "interface_type", "dynamic", "moveable", "resizable",
            "optimization_priority", "container", "containers", "render_type",
            "http_content_type", "remote_methods", "handlers", "languages", "version")
    else:
        subject = managers.memory.applications.search(uuid_or_name)
        if subject:
            entity = APPLICATION
            names = ("id", "name", "owner", "password", "active", "index",
                "server_version", "scripting_language", "default_language")
        else:
            console.error("unable to find application or type with such uuid or name")
            return

    try:
        with section("summary"):
            show("entity", entity)
            for name in names:
                value = getattr(subject, name)
                explanation = explain(name, value)
                if explanation:
                    value = explanation
                elif isinstance(value, basestring):
                    value = value or "<empty>"
                elif isinstance(value, (tuple, list)):
                    if value:
                        value = ", ".join(item for item in sorted(value))
                    else:
                        value = "<empty>"
                else:
                    value = repr(value)
                show(name.replace("_", " "), value)

        if entity is TYPE:
            with section("attributes"):
                for attribute in subject.attributes.itervalues():
                    name = attribute.name.replace("_", " ")
                    if description:
                        show(name, describe(subject, attribute))
                    else:
                        show(name, interface(subject, attribute))

    except Exception as error:
        console.error("unable to show %s: %s" % (entity, error))
        raise
