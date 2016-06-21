
from collections import MutableSet
from utils.properties import lazy, roproperty, rwproperty
from ..generic import MemoryBase


class MemoryStructureLevelSketch(MemoryBase, MutableSet):

    @lazy
    def _items(self):
        return set()

    def __init__(self, owner, name):
        self._owner = owner
        self._name = name

    owner = roproperty("_owner")
    name = rwproperty("_name")

    def add(self, item):
        with self._owner.owner.lock:
            self._items.add(item)

    def discard(self, item):
        with self._owner.owner.lock:
            self.__dict__.get("_items", ()).discard(item)

    def __contains__(self, item):
        return item in self.__dict__.get("_items", ())

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __invert__(self):
        self.__class__ = MemoryStructureLevel
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "structure level",
            "\"%s\"" % self._name if self._name else None,
            "sketch of %s" % self._owner)))


class MemoryStructureLevel(MemoryStructureLevelSketch):

    name = rwproperty("_name", notify="_owner.owner.autosave")

    def compose(self, ident=u"", file=None):
        items = self.__dict__.get("_items")
        attributes = u" Name=\"%s\"" % self._name.encode("xml")
        if items:
            file.write(u"%s<Level%s>\n" % (ident, attributes))
            for item in items:
                file.write(u"%s\t<Object ID=\"%s\"/>" % (ident, item.id))
            file.write(u"%s</Level>\n" % ident)
        else:
            file.write(u"%s<Level%s/>\n" % (ident, attributes))

    def add(self, item):
        super(MemoryStructureLevel, self).add(item)
        self._owner.owner.autosave()

    def discard(self, item):
        super(MemoryStructureLevel, self).discard(item)
        self._owner.owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "structure level",
            "\"%s\"" % self._name if self._name else None,
            "of %s" % self._owner)))
