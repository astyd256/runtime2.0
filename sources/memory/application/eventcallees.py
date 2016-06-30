
from collections import MutableSequence
from uuid import uuid4
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .binding import MemoryBindingSketch


EMPTY_LIST = []


class MemoryEventCalleesSketch(MemoryBase, MutableSequence):

    @lazy
    def _items(self):
        return []

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")

    def new_sketch(self, target_object, name, parameters=None, restore=False):
        return MemoryBindingSketch(self.append, target_object, name, parameters=parameters)

    def insert(self, index, callee):
        self._items.insert(index, callee)

    def __getitem__(self, index):
        return self.__dict__.get("_items", EMPTY_LIST)[index]

    def __setitem__(self, index, callee):
        self._items[index] = callee

    def __delitem__(self, index):
        del self.__dict__.get("_items", EMPTY_LIST)[index]

    def __len__(self):
        return len(self.__dict__.get("_items", EMPTY_LIST))

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

    def insert(self, index, callee):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).insert(index, callee)
            self._owner.owner.autosave()

    def __setitem__(self, index, callee):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).__setitem__(index, callee)
            self._owner.owner.autosave()

    def __delitem__(self, index):
        with self._owner.owner.lock:
            super(MemoryEventCallees, self).__delitem__(index)
            self._owner.owner.autosave()

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return "callees of %s" % self._owner
