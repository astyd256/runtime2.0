
from utils.properties import roproperty, rwproperty
from utils import verificators
from scripting.executable import LibraryStorage, LibraryExecutable
from ..generic import MemoryBase


class MemoryLibrarySketch(MemoryBase, LibraryStorage, LibraryExecutable):

    def __init__(self, callback, owner):
        self._callback = callback
        self._owner = owner
        self._id = None
        self._name = None
        self._top = 0
        self._left = 0
        self._state = False

    lock = property(lambda self: self._owner.lock)
    owner = roproperty("_owner")
    application = property(lambda self: self._owner.application)

    name = rwproperty("_name")

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
        # NOTE: currently is read-only property
        #       in the future must rename source and other files on rename...
        #       also need to unlink and reregister in sys.modules
        raise NotImplementedError

        if self._name == value:
            return

        if not verificators.name(value):
            raise Exception("Invalid name: %r" % value)

        with self._owner.lock:
            self._name = self._callback(self, value)
            self._owner.autosave()

    def _get_source_code(self):
        with self._owner.lock:
            return super(MemoryLibrary, self)._get_source_code()

    def _set_source_code(self, value):
        with self._owner.lock:
            super(MemoryLibrary, self)._set_source_code(value)

    name = rwproperty("_name")
    source_code = property(_get_source_code, _set_source_code)

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
