
import managers
import file_access
from utils.properties import lazy, roproperty
from .generic import CodeStorage


class FileCodeStorage(CodeStorage):

    @lazy
    def _location(self):
        raise NotImplementedError

    location = roproperty("_location")

    def _exists(self, extension):
        return managers.file_manager.exists(file_access.FILE, None, self._location + extension)

    def _read(self, extension):
        with managers.file_manager.open(file_access.FILE, None, self._location + extension, mode="rU", encoding="utf8") as file:
            return file.read()

    def _write(self, extension, value):
        with managers.file_manager.open(file_access.FILE, None, self._location + extension, mode="w", encoding="utf8") as file:
            return file.write(value)

    def _delete(self, extension):
        managers.file_manager.delete(file_access.FILE, None, self._location + extension)
