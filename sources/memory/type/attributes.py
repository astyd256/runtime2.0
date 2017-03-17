
from collections import OrderedDict, Mapping
from utils.properties import weak, roproperty
from ..generic import MemoryBase
from .attribute import MemoryTypeAttributeSketch


@weak("_owner")
class MemoryTypeAttributes(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        # NOTE: OrderedDict used to make debug more convenient
        self._items = OrderedDict()  # {}

    owner = roproperty("_owner")

    def on_complete(self, item):
        self._items[item.name] = item

    def new_sketch(self, restore=False):
        return MemoryTypeAttributeSketch(self)

    # unsafe
    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<Attributes>\n" % ident)
            for attribute in self._items.itervalues():
                attribute.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Attributes>\n" % ident)

    def __getitem__(self, name):
        return self._items[name]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "attributes of %s" % self._owner
