
import settings
import managers
import file_access

from utils.properties import roproperty, rwproperty
from utils import verificators
from scripting.executable import SOURCE_CODE, Executable

from ..generic import MemoryBase


class MemoryLibrarySketch(MemoryBase, Executable):

    _name = None
    _top = 0
    _left = 0
    _state = False

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner

    lock = property(lambda self: self._owner.lock)
    owner = roproperty("_owner")
    application = property(lambda self: self._owner.application)

    scripting_language = property(lambda self: str(self._owner.application.scripting_language))
    package = property(lambda self: str(self._owner.application.id))
    signature = property(lambda self: "<%s library %s>" % (self.scripting_language, self.name.lower()))

    name = rwproperty("_name")

    def locate(self, entity):
        if entity is SOURCE_CODE or settings.STORE_BYTECODE:
            return managers.file_manager.locate(file_access.LIBRARY, self.application.id, self.name)
        else:
            return None

    def __invert__(self):
        self.__class__ = MemoryLibrary
        self._callback = self._callback(self)

        if self._name is None:
            raise Exception(u"Library require name")

        return self

    def __str__(self):
        return " ".join(filter(None, (
            "library",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner)))


class MemoryLibrary(MemoryLibrarySketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new library")

    def _set_name(self, value):
        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self._owner.lock:
            source_code = self.source_code
            self.cleanup(remove=True)
            self._name = self._callback(self, value)
            self.source_code = source_code
            self._owner.autosave()

    name = rwproperty("_name")

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        information = u"Name=\"%s\"" % self._name.encode("xml")
        if not shorter and self.source_code:
            file.write(u"%s<Library %s>\n" % (ident, information))
            file.write(u"%s\n" % self.source_code.encode("cdata"))
            file.write(u"%s</Library>\n" % ident)
        else:
            file.write(u"%s<Library %s/>\n" % (ident, information))

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "library",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._owner)))
