
from marshal import dumps, loads
import errno
import managers
import file_access
from ..constants import BYTECODE
from .generic import Storage


class FileStorage(Storage):

    def exists(self, entity):
        return managers.file_manager.exists(file_access.FILE, None, self.locate(entity))

    def read(self, entity):
        if entity is BYTECODE:
            mode, encoding = "rb", None
        else:
            mode, encoding = "rU", "utf8"

        try:
            with managers.file_manager.open(file_access.FILE, None,
                    self.locate(entity), mode=mode, encoding=encoding) as file:
                value = file.read()
        except Exception as error:
            if error.errno == errno.ENOENT:
                return
            else:
                raise

        if entity is BYTECODE:
            value = loads(value)

        return value

    def write(self, entity, value):
        if entity is BYTECODE:
            mode, encoding = "wb+", None
            value = dumps(value)
        else:
            mode, encoding = "w+", "utf8"

        with managers.file_manager.open(file_access.FILE, None,
                self.locate(entity), mode=mode, encoding=encoding) as file:
            return file.write(value)

    def delete(self, entity):
        managers.file_manager.delete(file_access.FILE, None, self.locate(entity))
