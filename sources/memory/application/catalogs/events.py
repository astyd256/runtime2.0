
from collections import Mapping
from ...generic import MemoryBase


MISSING = "MISSING"


class MemoryEventsCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection
        self._items = {}

    # unsafe
    def compose(self, ident=u"", file=None):
        if self._items:
            file.write(u"%s<Events>\n" % ident)
            for event in self._items.itervalues():
                event.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Events>\n" % ident)

    def __getitem__(self, key):
        return self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "events catalog of %s" % self._collection._owner


class MemoryEventsDynamicCatalog(MemoryBase, Mapping):

    def __init__(self, collection):
        self._collection = collection

    def __getitem__(self, key):
        item = self._collection._items.get(key, MISSING)
        if item is not MISSING:
            return item
        for subitem in self._collection._items.itervalues():
            item = subitem.events.catalog.get(key, MISSING)
            if item is not MISSING:
                return item
        raise KeyError(key)

    def __iter__(self):
        for item in self._collection._items:
            yield item
        for subitem in self._collection._items.itervalues():
            for item in subitem.events.catalog:
                yield item

    def __len__(self):
        return sum(
            (len(item.events.catalog) for item in self._collection._items.itervalues()),
            len(self._collection._items))

    def __str__(self):
        return "events dynamic catalog of %s" % self._collection._owner
