
from collections import Sequence
from utils.properties import roproperty
from ..generic import MemoryBase
from .actionparameter import MemoryTypeActionParameterSketch


class MemoryTypeActionParameters(MemoryBase, Sequence):

    def __init__(self, owner):
        self._owner = owner
        self._items = []

    owner = roproperty("_owner")

    def new_sketch(self, restore=False):
        return MemoryTypeActionParameterSketch(self._items.append, self._owner)

    # unsafe
    def compose(self, ident=u"", file=None):
        if self.__dict__.get("_items"):
            file.write(u"%s<Parameters>\n" % ident)
            for parameter in self._items:
                parameter.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Parameters>\n" % ident)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __str__(self):
        return "parameters of %s" % self._owner
