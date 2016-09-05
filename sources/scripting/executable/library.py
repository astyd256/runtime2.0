
import managers
import file_access

from utils.properties import lazy

from .constants import LISTING
from .storage import FileStorage
from .generic import Executable


class LibraryStorage(FileStorage):

    def locate(self, entity):
        return managers.file_manager.locate(file_access.LIBRARY,
            self.application.id, self.name) + self.subsystem.extensions[entity]


class LibraryExecutable(Executable):

    @lazy
    def scripting_language(self):
        return str(self.application.scripting_language)

    @lazy
    def package(self):
        return str(self.application.id)

    @lazy
    def signature(self):
        return self.locate(LISTING) or "<%s library %s:%s>" % (self.scripting_language, self.name.lower())
