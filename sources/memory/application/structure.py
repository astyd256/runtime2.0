
from collections import Mapping
from utils.properties import lazy, roproperty, rwproperty
from ..generic import MemoryBase
from .structurelevel import MemoryStructureLevel, MemoryStructureLevelSketch


class MemoryStructureSketch(MemoryBase, Mapping):

    @lazy
    def _items(self):
        return {}

    def __init__(self, owner):
        self._owner = owner
        self._resource = None
        self._top = 0
        self._left = 0
        self._state = 0

    owner = roproperty("_owner")
    resource = rwproperty("_resource")
    top = rwproperty("_top")
    left = rwproperty("_left")
    state = rwproperty("_state")

    def __invert__(self):
        if "_items" in self.__dict__:
            for item in self._items.itervalues():
                ~item
        self.__class__ = MemoryStructure
        return self

    def __getitem__(self, name):
        try:
            return self._items[name]
        except KeyError:
            return self._items.setdefault(name, MemoryStructureLevelSketch(self, name))

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "structure sketch of %s" % self._owner


class MemoryStructure(MemoryStructureSketch):

    resource = rwproperty("_resource", notify="_owner.autosave")
    top = rwproperty("_top", notify="_owner.autosave")
    left = rwproperty("_left", notify="_owner.autosave")
    state = rwproperty("_state", notify="_owner.autosave")

    def compose(self, ident=u"", file=None):
        information = u"ID=\"%s\"%s Top=\"%s\" Left=\"%s\" State=\"%s\"" % \
            (self._owner.id, u" ResourceID=\"%s\"" % self._resource if self._resource else u"",
                self._top, self._left, self._state)
        if self.__dict__.get("_items"):
            file.write(u"%s<Object %s>\n" % (ident, information))
            for item in self._items.itervalues():
                item.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Object>\n" % ident)
        else:
            file.write(u"%s<Object %s/>\n" % (ident, information))

    def __getitem__(self, key):
        with self._owner.lock:
            try:
                return self._items[key]
            except KeyError:
                return self._items.setdefault(key, MemoryStructureLevel(self, key))

    def __str__(self):
        return "structure of %s" % self._owner
