
from collections import Mapping

import settings
import file_access
import managers

from utils import verificators
from utils.properties import roproperty
from logs import log

from ..auxiliary import parse_index_line
from ..generic import MemoryBase
from .type import MemoryTypeSketch


NOT_LOADED = "NOT LOADED"


class MemoryTypes(MemoryBase, Mapping):

    def __init__(self, owner):
        self._owner = owner
        self._items = {}
        self._index = {}
        self._lazy = True

    owner = roproperty("_owner")

    def new_sketch(self, restore=False):

        def on_complete(item):
            with self._owner._lock:
                self._items[item.id] = item
                self._index[item.name] = item.id

        return MemoryTypeSketch(on_complete)

    def save(self):
        if self._lazy:
            self._discover(full=True)
        data = "\n".join("%s:%s" % (uuid, name) for name, uuid in self._index.iteritems())
        managers.file_manager.write(file_access.FILE, None, settings.INDEX_LOCATION, data)

    def _load(self, uuid):
        with self._owner._lock:
            item = self._owner.load_type(uuid, silently=True)
            self._items[uuid] = item
            self._index[item.name] = uuid
            return item

    def _discover(self, full=False, load=False):
        with self._owner._lock:
            if managers.file_manager.exists(file_access.FILE, None, settings.INDEX_LOCATION):
                data = managers.file_manager.read(file_access.FILE, None, settings.INDEX_LOCATION)
                for line in data.splitlines():
                    try:
                        uuid, name = parse_index_line(line)
                    except ValueError:
                        log.warning("Ignore erroneous index entry: %s" % line)
                        continue
                    self._items.setdefault(uuid, NOT_LOADED)
                    self._index.setdefault(name, uuid)

            listing = managers.file_manager.list(file_access.TYPE)
            for uuid in listing:
                try:
                    verificators.uuid(uuid)
                except ValueError:
                    log.warning("Ignore erroneous directory: %s" % uuid)
                    continue
                self._items.setdefault(uuid, NOT_LOADED)

            if full and len(self._items) > len(self._index):
                unknown = set(self._items.keys()) - set(self._index.values())
                for uuid in unknown:
                    self._load(uuid)

            if load:
                for uuid, item in self._items.iteritems():
                    if item is NOT_LOADED:
                        self._load(uuid)

            self._lazy = False

    def search(self, uuid_or_name):
        with self._owner._lock:
            try:
                return self[uuid_or_name]
            except KeyError:
                if self._lazy:
                    self._discover(full=True)
                try:
                    uuid = self._index[uuid_or_name]
                except KeyError:
                    return None
                else:
                    return self[uuid]

    def unload(self, uuid, remove=False):
        with self._owner._lock:
            if remove:
                name = self._items.pop(uuid).name
                self._index.pop(name, None)
                self.save()
            else:
                self._items[uuid] = NOT_LOADED

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
                self._discover(load=True)
            return iter(self._items)

    def __len__(self):
        with self._owner._lock:
            if self._lazy:
                self._discover()
            return len(self._items)

    def __str__(self):
        return "types%s" % ":lazy" if self._lazy else ""
