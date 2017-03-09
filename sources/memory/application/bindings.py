
from weakref import ref
from collections import MutableMapping
from uuid import uuid4
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .catalogs import MemoryBindingsCatalog, MemoryBindingsDynamicCatalog
from .binding import MemoryBindingSketch, MemoryBindingRestorationSketch


class MemoryBindings(MemoryBase, MutableMapping):

    @lazy
    def _items(self):
        return {}

    @lazy
    def _all_items(self):
        return self._owner.application.bindings.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryBindingsCatalog(self)
        else:
            return MemoryBindingsDynamicCatalog(self)

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")

    def on_complete(self, item, restore):
        if item._target_object.virtual:
            return

        with self._owner.lock:
            self._items[item.id] = item

            if not self._owner.virtual:
                self._all_items[item.id] = item

        if not restore:
            if not item._target_object.virtual:
                self._owner.autosave()

    def new_sketch(self, target_object, name, parameters=None, restore=False):
        return (MemoryBindingRestorationSketch if restore
            else MemoryBindingSketch)(self, target_object, name, parameters=parameters)

    def new(self, target_object, name, parameters=None):
        item = self.new_sketch(target_object, name, parameters=parameters)
        item.id = str(uuid4())
        return ~item

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
            del self._all_items[item.id]
            if not item.target_object.virtual:
                self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "bindings of %s" % self._owner
