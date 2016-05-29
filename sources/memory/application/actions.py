
from collections import MutableMapping
from uuid import uuid4
from utils.generators import generate_unique_name
from utils.properties import lazy, roproperty
from ..generic import MemoryBase
from .catalogs import MemoryActionsCatalog, MemoryActionsDynamicCatalog
from .action import MemoryActionSketch, MemoryActionDuplicationSketch


NAME_BASE = "action"


class MemoryActions(MemoryBase, MutableMapping):

    def __init__(self, owner):
        self._owner = owner

    @lazy
    def _items(self):
        return {}

    @lazy
    def _items_by_name(self):
        return {}

    @lazy
    def _all_items(self):
        return self._owner.application.actions.catalog._items

    @lazy
    def _catalog(self):
        if self._owner.is_application:
            return MemoryActionsCatalog(self)
        else:
            return MemoryActionsDynamicCatalog(self)

    owner = roproperty("_owner")
    catalog = roproperty("_catalog")
    generic = roproperty("_generic")

    def _on_complete(self, item):
        with self._owner.lock:
            if not item.name or item.name in self._items_by_name:
                item.name = generate_unique_name(item.name or NAME_BASE, self._items_by_name)

            self._items[item.id] = item
            self._items_by_name[item.name] = item

            if not self._owner.virtual:
                self._all_items[item.id] = item

            return self._on_rename

    def _on_rename(self, item, name):
        with self._owner.lock:
            del self._items_by_name[item.name]
            self._items_by_name[name] = item

    def new_sketch(self):
        return MemoryActionSketch(self._on_complete, self._owner)

    def new(self, name=None):
        item = self.new_sketch()
        item.id = str(uuid4())
        with self._owner.lock:
            if not name or name in self._items_by_name:
                name = generate_unique_name(name or NAME_BASE, self._items_by_name)

            item.name = name
            ~item

            self._owner.invalidate(contexts=(item.id, item.name), downward=True, upward=True)
            self._owner.autosave()
        return item

    # unsafe
    def compose(self, ident=u"", file=None):
        actions = tuple(action for action in self._items.itervalues()
            if action.source_code or action.name not in self._owner.generic)
        if actions:
            file.write(u"%s<Actions>\n" % ident)
            for action in actions:
                action.compose(ident=ident + u"\t", file=file)
            file.write(u"%s</Actions>\n" % ident)

    def clear(self):
        if "_items" in self.__dict__:
            with self._owner.lock:
                contexts = set(self._items)
                contexts.update(self._items_by_name)

                for name in self._items:
                    del self._all_items[name]
                del self._items
                del self._items_by_name

                self._owner.invalidate(contexts=contexts, downward=True, upward=True)
                self._owner.autosave()

    def __iadd__(self, actions):
        if "_items" in actions.__dict__:
            with self._owner.lock:
                contexts = set()
                for item in actions._items.itervalues():
                    copy = MemoryActionDuplicationSketch(self._on_complete, self._owner, item)
                    ~copy
                    contexts.update({item.id, item.name})
                self._owner.invalidate(contexts=contexts, downward=True, upward=True)
        return self

    def __getitem__(self, key):
        return self._items.get(key) or self._items_by_name[key]

    def __setitem__(self, key, value):
        raise Exception(u"Use 'new' to create new action")

    def __delitem__(self, key):
        with self._owner.lock:
            item = self._items.get(key) or self._items_by_name[key]
            del self._items[item.id]
            del self._items_by_name[item.name]
            del self._all_items[item.id]
            self._owner.invalidate(contexts=(item.id, item.name), downward=True, upward=True)
            self._owner.autosave()

    def __iter__(self):
        return iter(self.__dict__.get("_items", ()))

    def __len__(self):
        return len(self.__dict__.get("_items", ()))

    def __str__(self):
        return "actions of %s" % self._owner
