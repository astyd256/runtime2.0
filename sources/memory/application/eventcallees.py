
from collections import MutableSet
from uuid import uuid4
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .binding import MemoryBindingSketch


class MemoryEventCalleesSketch(MemoryBase, MutableSet):

    @lazy
    def _items(self):
        return set()

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")

    def new_sketch(self, target_object, name, parameters=None):
        return MemoryBindingSketch(self.add, target_object, name, parameters=parameters)

    def add(self, item):
        self._items.add(item)

    def discard(self, item):
        self.__dict__.get("_items", ()).discard(item)

    def __contains__(self, item):
        return item in self.__dict__.get("_items", ())

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __invert__(self):
        self.__class__ = MemoryEventCallees
        return self

    def __str__(self):
        return "callees sketch of %s" % self._owner


class MemoryEventCallees(MemoryEventCalleesSketch):

    def new(self, target_object, name, parameters=None):
        item = self.new_sketch(target_object, name, parameters=parameters)
        item.id = str(uuid4())
        return ~item

    def add(self, item):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).add(item)
            self._owner.owner.autosave()

    def discard(self, item):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).discard(item)
            self._owner.owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return "callees of %s" % self._owner
