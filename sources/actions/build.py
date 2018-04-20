
from startup import builder
from .auxiliary import warn


def run():
    """
    build runtime binary modules
    """
    if builder.show_warning:
        warn("must be called from the command line")
