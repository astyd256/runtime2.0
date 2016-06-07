
import settings
import managers
import file_access

from utils.properties import lazy, roproperty
from memory import PYTHON_EXTENSION

from .generic import Executable
from .code import PythonCode


class Module(Executable):

    @lazy
    def _location(self):
        return managers.file_manager.locate(file_access.MODULE, self._type.id, self._name)

    @lazy
    def _name(self):
        return settings.TYPE_MODULE_NAME

    @lazy
    def _extension(self):
        return PYTHON_EXTENSION

    def __init__(self, type):
        self._type = type

    owner = type = roproperty("_type")

    def __str__(self):
        return "module %s" % self._type.id


class PythonModule(Module, PythonCode):
    pass
