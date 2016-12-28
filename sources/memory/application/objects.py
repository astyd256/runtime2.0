
from weakref import ref
from collections import OrderedDict, MutableMapping
from itertools import islice
from uuid import uuid4

import managers
import security

from utils.exception import VDOMSecurityError
from utils.generators import generate_unique_name
from utils.properties import lazy, weak, roproperty

from ..generic import MemoryBase
from .catalogs import MemoryObjectsCatalog, MemoryObjectsDynamicCatalog


def wrap_rename(instance):
    instance = ref(instance)

    def on_rename(item, name):
        self = instance()
        with self._owner.lock:
            del self._items_by_name[item.name]
            if name in self._items_by_name:
                name = generate_unique_name(name, self._items_by_name)
            self._items_by_name[name] = item
            return name

    return on_rename


def wrap_complete(instance, restore):
    instance = ref(instance)

    def on_complete(item):
        self = instance()
        with self._owner.lock:
            if item._name is None or item._name in self._items_by_name:
                item._name = generate_unique_name(item._name or item._type.name, self._items_by_name)
            item._order = len(self._items)

            if item._virtual == self._owner.virtual:
                self._items[item.id] = item
                self._items_by_name[item.name] = item

            if not item._virtual:
                self._all_items[item.id] = item

            if not restore:
                managers.dispatcher.dispatch_handler(item, "on_create")
                if self._owner.is_object and item._virtual == self._owner.virtual:
                    managers.dispatcher.dispatch_handler(self._owner, "on_insert", item)
                    self._owner.invalidate(upward=True)
                item.autosave()

            return wrap_rename(self)

    return on_complete


@weak("_owner")
class MemoryObjects(MemoryBase, MutableMapping):

    @lazy
    def _items(self):
        return OrderedDict()

    @lazy
    def _items_by_name(self):
        return {}

    @lazy
    def _all_items(self):
        return self._owner.application.objects.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryObjectsCatalog(self)
        else:
            return MemoryObjectsDynamicCatalog(self)

    def __init__(self, owner):
        self._owner = owner

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")

    def new_sketch(self, type, virtual=False, attributes=None, restore=False):
        return MemoryObjectSketch(wrap_complete(self, restore), type,
            self._owner.application, None if self._owner.is_application else self._owner,
            virtual=virtual, attributes=attributes)

    def new(self, type, name=None, virtual=False, attributes=None):
        item = self.new_sketch(type, virtual=virtual, attributes=attributes)
        item.id = str(uuid4())
        item.name = name
        return ~item

    def select(self, *names):
        result = self._owner
        for name in names:
            result = result.objects._items_by_name.get(name)
            if result is None:
                return None
        return result

    # unsafe
    def compose(self, ident=u"", file=None, shorter=False):
        with self._owner.lock:
            if self.__dict__.get("_items"):
                file.write(u"%s<Objects>\n" % ident)
                for object in self._items.itervalues():
                    object.compose(ident=ident + u"\t", file=file, shorter=shorter)
                file.write(u"%s</Objects>\n" % ident)

    def __iadd__(self, another):
        if self._owner.is_application:
            raise Exception(u"Use 'new' to create new top-level container")

        if "_items" in another.__dict__:
            with self._owner.lock:
                copy = None

                for item in another._items.itervalues():
                    copy = MemoryObjectDuplicationSketch(wrap_complete(self, False),
                        self._owner.application, None if self._owner.is_application else self._owner,
                        item)
                    copy.id = str(uuid4())
                    copy.name = item.name
                    ~copy

                    managers.dispatcher.dispatch_handler(copy, "on_create")
                    if self._owner.is_object and copy.virtual == self._owner.virtual:
                        managers.dispatcher.dispatch_handler(self._owner, "on_insert", copy)

                if copy:
                    if self._owner.is_object and self._owner.virtual == copy.virtual:
                        self._owner.invalidate(upward=True)
                    copy.autosave()

        return self

    def __getitem__(self, key):
        return self._items.get(key) or self._items_by_name[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new object")

    def __delitem__(self, key):
        with self._owner.lock:
            item = self._items.get(key) or self._items_by_name[key]

            # dispatch events
            if self._owner.is_object and item.virtual == self._owner.virtual:
                managers.dispatcher.dispatch_handler(self._owner, "on_remove", item)
            managers.dispatcher.dispatch_handler(item, "on_delete")

            # delete all child objects
            item.objects.clear()

            # cleanup structure
            if item.structure:
                for container in self._owner.application.objects.itervalues(): # pages
                    if item is container:
                        continue
                    for level in container.structure.itervalues():
                        if item in level:
                            level.remove(item)

            # remove events
            item.events.clear()
            # bindings = (binding for binding in self._owner.application.bindings.itervalues()
            #     if binding.target_object == item)
            bindings = (binding for binding in self._owner.application.bindings.catalog.itervalues()
                if binding.target_object == item)
            for event in self._owner.application.events.catalog.itervalues():
                # event.callees -= bindings
                for binding in bindings:
                    while binding in event.callees:
                        event.callees.remove(binding)
            for binding in bindings:
                # del self._owner.application.bindings[binding.id]
                del binding.target_object.container.bindings[binding.id]

            # delete resources
            # NOTE: currently invalidate do this
            # managers.resource_manager.invalidate_resources(item.id)

            # delete source code and autosave
            item.invalidate(upward=True)
            item.autosave()

            # recalculate order for following objects
            index = self._items.keys().index(key)
            for another in islice(self._items.itervalues(), index + 1, None):
                another._order -= 1

            # remove from dictionaries
            del self._items[item.id]
            del self._items_by_name[item.name]
            if not item.virtual:
                del self._all_items[item.id]

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "objects of %s" % self._owner


from .object import MemoryObjectSketch, MemoryObjectDuplicationSketch
