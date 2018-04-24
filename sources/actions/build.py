
from startup import builder
from .auxiliary import warn


def run(list=False, cleanup=False, *extension):
    """
    build runtime binary modules
    :key switch list: show availavle exensions
    :key switch cleanup: cleanup building directories
    :arg extension: optional extensions to build
    """
    if builder.show_warning:
        warn("must be called from the command line")
