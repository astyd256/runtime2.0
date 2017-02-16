
from memory import PYTHON_LANGUAGE, VSCRIPT_LANGUAGE

from .python import PythonBytecode
from .vscript import VScriptBytecode


CLASSES = {PYTHON_LANGUAGE: PythonBytecode, VSCRIPT_LANGUAGE: VScriptBytecode}


def select(language):
    try:
        return CLASSES[language]
    except KeyError:
        raise Exception("Unknown scripting language: \"%s\"" % language)
