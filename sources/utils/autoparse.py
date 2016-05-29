
import inspect
import re

from types import FunctionType, ModuleType
from itertools import izip, chain
from argparse import OPTIONAL, REMAINDER, ArgumentParser, ArgumentTypeError, HelpFormatter, Action

import utils.verificators
from utils.structure import Structure


SUPRESS_HELP = "SUPRESS HELP"
DOCSTRING_HELP_REGEX = re.compile(r"^\s*(?P<help>[^:].*)?$", re.MULTILINE)
DOCSTRING_ARGUMENT_REGEX = re.compile(r"^:param(?:\s+(?P<type>\w+))?\s+(?P<name>\w+):\s?(?P<help>.*)$", re.MULTILINE)
DEFAULT_LETTERS = False
SWITCH_VALUES = {
    "0": False, "1": True,
    "no": False, "yes": True,
    "off": False, "on": True,
    "false": False, "true": True,
    "disabled": False, "enabled": True
}


def switch(value):
    try:
        return SWITCH_VALUES[str(value).lower()]
    except KeyError:
        raise ValueError("Not an switch")


def make_verificator(verificator):
    def wrapper(value):
        try:
            return verificator(value)
        except ValueError as error:
            raise ArgumentTypeError(str(error))
    wrapper.name = verificator.__name__
    wrapper.verificator = verificator
    return wrapper


class HiddenHelpFormatter(HelpFormatter):

    def _format_action(self, action):
        if action.help is SUPRESS_HELP:
            return ""
        else:
            return super(HiddenHelpFormatter, self)._format_action(action)


class StoreMandatoryAction(Action):

    def __init__(self, option_strings, dest, nargs=None, const=None,
            default=None, type=None, choices=None, required=False, help=None, metavar=None):
        if nargs == 0:
            raise ValueError('nargs for store actions must be > 0; if you '
                'have nothing to store, actions such as store true or store const may be more appropriate')
        if const is not None and nargs != OPTIONAL:
            raise ValueError('nargs must be %r to supply const' % OPTIONAL)
        super(StoreMandatoryAction, self).__init__(option_strings=option_strings, dest=dest, nargs=nargs, const=const,
            default=default, type=type, choices=choices, required=required, help=help, metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) == self.default:
            setattr(namespace, self.dest, values)


verificators = {native.__name__: make_verificator(native)
    for native in (int, long, float, complex, str, unicode, bool, tuple, list, dict, set, switch)}

for name in dir(utils.verificators):
    native = getattr(utils.verificators, name)
    if isinstance(native, FunctionType):
        verificators[name] = make_verificator(native)


def autoparse(alias, routine, subparsers, letters=None):
    names, arguments, keywords, defaults = inspect.getargspec(routine)
    metadata, description = {}, None

    index = len(names) - (len(defaults) if defaults else 0)
    mandatory = names[:index]
    optional = names[index:]

    docstirng = inspect.getdoc(routine)
    if docstirng:
        match = DOCSTRING_HELP_REGEX.match(docstirng)
        if match:
            description = match.group("help")
        matches = DOCSTRING_ARGUMENT_REGEX.finditer(docstirng)
        for match in matches:
            media = match.group("type")
            metadata[match.group("name")] = media, verificators.get(media), match.group("help")

    subparser = subparsers.add_parser(alias, help=description, formatter_class=HiddenHelpFormatter)

    for name in mandatory:
        media, verificator, description = metadata.get(name, (None, None, None))
        subparser.add_argument(name, type=verificator, help=description)

    if defaults:
        letters = set("h") if letters or DEFAULT_LETTERS else None
        for name, default in izip(optional, defaults):
            media, verificator, description = metadata.get(name, (None, None, None))
            flags_keywords = {}

            if letters is None or name[0] in letters:
                flags = "--%s" % name,
            else:
                flags = "-%s" % name[0], "--%s" % name
                letters.add(name[0])

            if media == "switch":
                flags_keywords["action"] = "store_false" if default else "store_true"
            else:
                flags_keywords["type"] = verificator
                flags_keywords["metavar"] = "<%s>" % (media or "str")  # (media or "str").upper()

            group = subparser.add_mutually_exclusive_group()
            group.add_argument(name, type=verificator, nargs=OPTIONAL,
                default=default, action=StoreMandatoryAction, help=SUPRESS_HELP)
            group.add_argument(*flags, help=description, **flags_keywords)

    if arguments:
        subparser.add_argument(arguments, nargs=REMAINDER)

    return routine, names, arguments


class AutoArgumentParser(ArgumentParser):

    def __init__(self, *arguments, **keywords):
        package = keywords.pop("package", None)
        module = keywords.pop("module", None)
        alias = keywords.pop("alias", None)
        super(AutoArgumentParser, self).__init__(*arguments, **keywords)
        if module:
            self._package = package or module.__package__ + "."
            self._name = ":%s:" % (alias or module.__name__)
            self._parsers = {}
            self._repository = {}

            subparsers = self.add_subparsers(dest=self._name)

            for name in dir(module):
                submodule = getattr(module, name)
                if not isinstance(submodule, ModuleType):
                    continue
                if not (submodule.__package__ and (submodule.__package__ + ".").startswith(self._package)):
                    continue

                description = submodule.__doc__.strip() if submodule.__doc__ else None
                run = getattr(submodule, "run", None)

                if isinstance(run, FunctionType):
                    self._repository[name] = autoparse(name, run, subparsers)
                elif run is None and submodule.__package__.endswith(submodule.__name__):
                    self._parsers[name] = subparsers.add_parser(name, help=description,
                        package=self._package, module=submodule, alias=name,
                        formatter_class=HiddenHelpFormatter)
        else:
            self._name = None

    def parse_args(self, args=None, namespace=None):
        arguments = super(AutoArgumentParser, self).parse_args(args=args, namespace=namespace)

        if self._name:
            subparser, parser = self, None
            while subparser:
                parser = subparser
                name = getattr(arguments, parser._name)
                subparser = parser._parsers.get(name)

            routine, names, remainder = parser._repository.get(name)
            arguments.action = Structure(
                name=name,
                run=routine,
                arguments=chain((getattr(arguments, name) for name in names),
                    getattr(arguments, remainder) if remainder else ()))

        return arguments
