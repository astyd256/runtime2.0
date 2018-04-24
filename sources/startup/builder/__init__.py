
from sys import exit
from argparse import ArgumentParser
from setuptools import Extension
from .builder import Builder, ReportBuilderFailureError


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
subparser = subparsers.add_parser("build")
subparser.add_argument("-l", "--list", action="store_true", dest="list", default=False,
    help="show availavle exensions")
subparser.add_argument("--cleanup", action="store_true", dest="cleanup", default=False,
    help="cleanup building directories")
subparser.add_argument("extensions", nargs="*", metavar="extension",
    help="optional extensions to build")

try:
    arguments = parser.parse_args()
except ArgumentsError as error:
    show_warning = True
else:
    show_warning = False
    try:
        builder = Builder(EXTENSIONS)
        if arguments.list:
            builder.list()
        elif arguments.cleanup:
            builder.cleanup()
        elif arguments.extensions:
            builder.build(*arguments.extensions)
        else:
            builder.build()
    except ReportBuilderFailureError:
        exit(1)
    except BaseException:
        raise
    else:
        exit(0)
