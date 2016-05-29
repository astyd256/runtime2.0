
from collections import Mapping

import settings
import file_access
import managers

from utils.properties import roproperty
from logs import log

from ..generic import MemoryBase
from .type import MemoryTypeSketch


NOT_LOADED = "NOT LOADED"


class MemoryTypes(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}
        self._lazy = True

    owner = roproperty("_owner")

    def _on_complete(self, item):
        with self._owner._lock:
            self._items[item.id] = item

    def new_sketch(self):
        return MemoryTypeSketch(self._on_complete)

    def _load(self, uuid):
        log.write("Load type %s" % uuid)
        with self._owner._lock:
            item = self._owner.load_type(uuid, silently=True)
            self._items[uuid] = item
            return item

    def _discover(self):
        uuids = managers.file_manager.list(file_access.TYPE)
        with self._owner._lock:
            for uuid in uuids:
                self._items.setdefault(uuid, NOT_LOADED)
            self._lazy = False

    def search(self, uuid_or_name):
        with self._owner._lock:
            try:
                return self[uuid_or_name]
            except KeyError:
                for item in self.itervalues():
                    if item.name == uuid_or_name:
                        return item

    def unload(self, id):
        with self._owner._lock:
            del self._items[id]

    def __getitem__(self, uuid):
        with self._owner._lock:
            try:
                item = self._items[uuid]
            except KeyError:
                if self._lazy and managers.file_manager.exists(file_access.TYPE, uuid, settings.TYPE_FILENAME):
                    item = NOT_LOADED
                else:
                    raise

            if item is NOT_LOADED:
                item = self._load(uuid)

            return item

    def __iter__(self):
        with self._owner._lock:
            if self._lazy:
                self._discover()
            for uuid, item in self._items.iteritems():
                if item is NOT_LOADED:
                    self._load(uuid)
            return iter(self._items)

    def __len__(self):
        with self._owner._lock:
            if self._lazy:
                self._discover()
            return len(self._items)

    def __str__(self):
        return "types%s" % ":lazy" if self._lazy else ""
