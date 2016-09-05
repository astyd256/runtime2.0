
from memory import PYTHON_LANGUAGE, VSCRIPT_LANGUAGE

import python
import vscript


MODULES = {
    PYTHON_LANGUAGE: python,
    VSCRIPT_LANGUAGE: vscript
}


def select(language):
    try:
        return MODULES[language]
    except KeyError:
        raise Exception("Unknown scripting language: \"%s\"" % language)
