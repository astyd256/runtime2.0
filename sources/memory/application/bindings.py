
from weakref import ref
from collections import MutableMapping
from uuid import uuid4
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .binding import MemoryBindingSketch


def wrap_complete(instance, restore):
    instance = ref(instance)

    def on_complete(item):
        self = instance()
        if item._target_object.virtual:
            return

        with self._owner.lock:
            self._items[item.id] = item

        if not restore:
            if not item._target_object.virtual:
                self._owner.autosave()

    return on_complete


class MemoryBindings(MemoryBase, MutableMapping):

    def __init__(self, owner):
        self._owner = owner

    @lazy
    def _items(self):
        return {}

    owner = roproperty("_owner")

    def new_sketch(self, target_object, name, parameters=None, restore=False):
        return MemoryBindingSketch(wrap_complete(self, restore), target_object, name, parameters=parameters)

    def new(self, target_object, name, parameters=None):
        item = self.new_sketch(target_object, name, parameters=parameters)
        item.id = str(uuid4())
        return ~item

    # unsafe
    def compose(self, ident=u"", file=None):
        if self._items:
            file.write(u"%s<Actions>\n" % ident)
            for binding in self._items.itervalues():
                binding.compose(ident=u"\t" + ident, file=file)
            file.write(u"%s</Actions>\n" % ident)

    def clear(self):
        with self._owner.lock:
            self._items.clear()
            self._owner.autosave()

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new binding")

    def __delitem__(self, key):
        with self._owner.lock:
            item = self._items.pop(key)
            if not item.target_object.virtual:
                self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "bindings of %s" % self._owner
