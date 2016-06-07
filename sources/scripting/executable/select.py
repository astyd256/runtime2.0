
from memory import PYTHON_LANGUAGE, VSCRIPT_LANGUAGE

from .module import PythonModule
from .library import PythonLibrary, VScriptLibrary
from .action import PythonAction, VScriptAction


MODULE_CLASSES = {
    PYTHON_LANGUAGE: PythonModule}

LIBRARY_CLASSES = {
    PYTHON_LANGUAGE: PythonLibrary,
    VSCRIPT_LANGUAGE: VScriptLibrary}

ACTION_CLASSES = {
    PYTHON_LANGUAGE: PythonAction,
    VSCRIPT_LANGUAGE: VScriptAction}


def select_module_class(language):
    try:
        return MODULE_CLASSES[language]
    except KeyError:
        raise Exception("Unknown scripting language: \"%s\"" % language)


def select_library_class(language):
    try:
        return LIBRARY_CLASSES[language]
    except KeyError:
        raise Exception("Unknown scripting language: \"%s\"" % language)


def select_action_class(language):
    try:
        return ACTION_CLASSES[language]
    except KeyError:
        raise Exception("Unknown scripting language: \"%s\"" % language)
