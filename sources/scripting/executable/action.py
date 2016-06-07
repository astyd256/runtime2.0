
from utils.properties import lazy, roproperty

from .generic import Executable
from .code import PythonCode, VScriptCode


class Action(Executable):

    @lazy
    def _package(self):
        return str(self._action.application.id)

    @lazy
    def _location(self):
        raise NotImplementedError

    @lazy
    def _extension(self):
        return self._action.scripting_extension

    @lazy
    def _source_code(self):
        return self._action.source_code

    def __init__(self, action, name):
        self._action = action
        self._name = name

    owner = action = roproperty("_action")

    def exists(self):
        raise NotImplementedError

    def __str__(self):
        return "action %s:%s" % (self._action.id, self._name)


class PythonAction(Action, PythonCode):
    pass


class VScriptAction(Action, VScriptCode):
    pass
