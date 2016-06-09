
import managers
import file_access

from utils.properties import lazy, roproperty
from memory import COMPILED_EXTENSION

from .storage import FileCodeStorage
from .code import PythonCode, VScriptCode
from .generic import Executable


class LibraryCodeStorage(FileCodeStorage):

    @lazy
    def _location(self):
        return managers.file_manager.locate(file_access.LIBRARY, self._application.id, self._name)


class Library(Executable, LibraryCodeStorage):

    @lazy
    def _package(self):
        return str(self._application.id)

    @lazy
    def _source_extension(self):
        return self._application.scripting_extension

    @lazy
    def _extension(self):
        return COMPILED_EXTENSION

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
