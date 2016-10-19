
import re
import settings as settings_module
from ..exceptions import OptionError


NAME_REGEX = re.compile("[A-Za-z][_0-9A-Za-z]*$")
VALUE_REGEX = re.compile("None$|True$|False$|[0-9]+$|\"(?:\\\\\"|[^\"\\\\])*\"$")


def settings(options):
    for name, value in options.iteritems():
        if not NAME_REGEX.match(name):
            raise OptionError("Incorrect name")
        if not VALUE_REGEX.match(value):
            raise OptionError("Incorrect value")
        if not hasattr(settings_module, name):
            raise OptionError("Unknown option: %s" % name)
        setattr(settings_module, name, eval(value))
    yield "<reply/>"
