
import managers
import file_access
from utils.properties import lazy


class Executable(object):

    @lazy
    def _package(self):
        return None

    @lazy
    def _location(self):
        raise NotImplementedError

    @lazy
    def _name(self):
        raise NotImplementedError

    @lazy
    def _extension(self):
        raise NotImplementedError

    @lazy
    def _source_code(self):
        with managers.file_manager.open(file_access.FILE, self._location + self._extension, mode="rU", encoding="utf8") as file:
            return file.read()

    def exists(self):
        return managers.file_manager.exists(file_access.FILE, self._location + self._extension)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return "<%s %s at 0x%08X>" % (self._scripting_language, self, id(self))
