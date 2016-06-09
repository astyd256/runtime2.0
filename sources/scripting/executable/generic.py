
from utils.properties import lazy, roproperty


class Executable(object):

    @lazy
    def _package(self):
        return None

    @lazy
    def _name(self):
        raise NotImplementedError

    @lazy
    def _source_extension(self):
        raise NotImplementedError

    @lazy
    def _extension(self):
        raise NotImplementedError

    @lazy
    def _source_code(self):
        return self._read(self._source_extension)

    package = roproperty("package")
    name = roproperty("name")
    source_extension = roproperty("_source_extension")
    source_code = roproperty("_source_code")

    def exists(self):
        return self._exists(self._source_extension)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return "<%s %s at 0x%08X>" % (self._scripting_language, self, id(self))
