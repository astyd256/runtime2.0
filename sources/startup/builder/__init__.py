
from sys import exit
from argparse import ArgumentParser
from setuptools import Extension
from .builder import Builder


EXTENSIONS = {
    "vdomxml": Extension("memory.vdomxml._loads",
        sources=["memory/vdomxml/loads.c"],
        include_dirs=["memory/vdomxml/include"])
}


class ArgumentsError(Exception):
    pass


class ExceptionalArgumentParser(ArgumentParser):

    def error(self, message):
        raise ArgumentsError(message)


parser = ExceptionalArgumentParser(add_help=False)
parser.add_argument("-c", "--configure", dest="filename", default=None)
subparsers = parser.add_subparsers(dest="action")
subparsers.add_parser("build")

try:
    arguments, other = parser.parse_known_args()
except ArgumentsError as error:
    show_warning = True
else:
    show_warning = False
    builder = Builder(**EXTENSIONS)
    exit_code = 0 if builder.build(*other) else 1
    exit(exit_code)
