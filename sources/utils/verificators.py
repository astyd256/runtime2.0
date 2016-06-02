
import re


UUID_REGEX = re.compile(r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$", re.IGNORECASE)
NAME_REGEX = re.compile(r"^[A-Z][A-Z\d_]*$", re.IGNORECASE)
UUID_OR_NAME_REGEX = re.compile(r"^(?:[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})|(?:[A-Z][A-Z\d_]*)$", re.IGNORECASE)
UUID_OR_NONE_REGEX = re.compile(r"^(?:[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})|(?:none)$", re.IGNORECASE)
SIZE_REGEX = re.compile(r"^(?P<size>[0-9]+)(?P<measure>[KM])?$", re.IGNORECASE)


def port(value):
    try:
        value = int(value)
    except ValueError:
        raise ValueError("Port must be a number")
    if value < 0:
        raise ValueError("Port must be greater then zero")
    return value


def uuid(value):
    if not UUID_REGEX.match(value):
        raise ValueError("Not an unique identifier")
    return value


def name(value):
    if not NAME_REGEX.match(value):
        raise ValueError("Not a name")
    return value


def uuid_or_name(value):
    if not UUID_OR_NAME_REGEX.match(value):
        raise ValueError("Not an unique identifier or name")
    return value


def uuid_or_none(value):
    if not UUID_OR_NONE_REGEX.match(value):
        raise ValueError("Not an unique identifier or none")
    return value


def size(value):
    match = SIZE_REGEX.match(value)
    if not match:
        raise ValueError("Not a size")

    size = match.group("size")
    measure = match.group("measure")
    if measure == "K":
        size *= 1024
    elif measure == "M":
        size *= 1024 * 1024

    return size
