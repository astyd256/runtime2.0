
from collections import Mapping
from utils.properties import roproperty
from ..generic import MemoryBase
from .event import MemoryTypeEventSketch


class MemoryTypeEvents(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}

    owner = roproperty("_owner")

    def new_sketch(self, restore=False):

        def on_comlete(item):
            self._items[item.name] = item

        return MemoryTypeEventSketch(on_comlete, self._owner)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "events of %s" % self._owner


class MemoryTypeUserInterfaceEvents(MemoryTypeEvents):

    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<UserInterfaceEvents>\n" % ident)
            for event in self._items.itervalues():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</UserInterfaceEvents>\n" % ident)

    def __str__(self):
        return "user interface events of %s" % self._owner


class MemoryTypeObjectEvents(MemoryTypeEvents):

    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<ObjectEvents>\n" % ident)
            for event in self._items.itervalues():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</ObjectEvents>\n" % ident)

    def __str__(self):
        return "object events of %s" % self._owner
