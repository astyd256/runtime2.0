
from collections import Mapping
from uuid import uuid4

import settings
import managers
import file_access

from utils import verificators
from logs import log

from ..generic import MemoryBase
from .application import MemoryApplicationSketch


DEFAULT_APPLICATION_NAME = "Application"
NOT_LOADED = "NOT LOADED"


class MemoryApplications(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}
        self._lazy = True

    def _on_complete(self, item):
        with self._owner._lock:
            self._items[item.id] = item
            for object in item._objects.itervalues():
                managers.dispatcher.dispatch_handler(object, "on_startup")

    def new_sketch(self):
        return MemoryApplicationSketch(self._on_complete)

    def new(self):
        item = self.new_sketch()
        item.id = str(uuid4())
        with self._owner._lock:
            item.name = DEFAULT_APPLICATION_NAME
            return ~item

    def _load(self, uuid):
        log.write("Load application %s" % uuid)
        with self._owner._lock:
            item = self._owner.load_application(uuid, silently=True)
            self._items[uuid] = item
            return item

    def _discover(self):
        listing = managers.file_manager.list(file_access.APPLICATION)
        with self._owner._lock:
            for filename in listing:
                try:
                    verificators.uuid(filename)
                except ValueError:
                    continue
                self._items.setdefault(filename, NOT_LOADED)
            self._lazy = False

    def search(self, uuid_or_name):
        with self._owner._lock:
            try:
                return self[uuid_or_name]
            except KeyError:
                for item in self.itervalues():
                    if item.name.lower() == uuid_or_name or \
                            item.name.lower().startswith(uuid_or_name):
                        return item
                raise KeyError(uuid_or_name)

    def unload(self, uuid):
        with self._owner._lock:
            application = self._items[uuid]
            application.unimport_libraries()
            del self._items[uuid]

    def __getitem__(self, uuid):
        with self._owner._lock:
            try:
                item = self._items[uuid]
            except KeyError:
                if self._lazy and managers.file_manager.exists(file_access.APPLICATION, uuid, settings.APPLICATION_FILENAME):
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
        return "applications%s" % ":lazy" if self._lazy else ""
