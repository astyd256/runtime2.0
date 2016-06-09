
from utils.properties import lazy, roproperty
from memory import COMPILED_EXTENSION

from .storage import CodeStorage
from .code import PythonCode, VScriptCode
from .generic import Executable


class ActionCodeStorage(CodeStorage):

    def _exists(self, extension):
        return extension == self._source_extension

    def _read(self, extension):
        if extension != self._source_extension:
            raise Exception("Unable to read: \"%s\"" % extension)
        return self._action.source_code


class Action(Executable, ActionCodeStorage):

    @lazy
    def _package(self):
        return str(self._action.application.id)

    @lazy
    def _source_extension(self):
        return self._action.application.scripting_extension

    @lazy
    def _extension(self):
        return COMPILED_EXTENSION

    def __init__(self, action, name):
        self._action = action
        self._name = name

    owner = action = roproperty("_action")

    def __str__(self):
        return "action %s:%s" % (self._action.id, self._name)


class PythonAction(Action, PythonCode):
    pass


class VScriptAction(Action, VScriptCode):
    pass
