
import managers
import file_access

from utils.properties import lazy, roproperty

from .generic import Executable
from .code import PythonCode, VScriptCode


class Library(Executable):

    @lazy
    def _package(self):
        return str(self._application.id)

    @lazy
    def _location(self):
        return managers.file_manager.locate(file_access.LIBRARY, self._application.id, self._name)

    @lazy
    def _extension(self):
        return self._application.scripting_extension

    def __init__(self, application, name):
        self._application = application
        self._name = name

    owner = application = roproperty("_application")

    def __str__(self):
        return "library %s:%s" % (self._application.id, self._name)


class PythonLibrary(Library, PythonCode):
    pass


class VScriptLibrary(Library, VScriptCode):
    pass
