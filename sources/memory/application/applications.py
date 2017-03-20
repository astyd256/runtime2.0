
from weakref import ref
from collections import Mapping
from itertools import chain
from threading import RLock, Event
from uuid import uuid4

import settings
import managers
import file_access

from utils import verificators
from utils.verificators import complies
from utils.properties import lazy, weak, roproperty
from logs import log

from ..generic import MemoryBase
from .application import MemoryApplicationSketch, MemoryApplicationRestorationSketch


DEFAULT_APPLICATION_NAME = "Application"


@weak("_owner")
class MemoryApplications(MemoryBase, Mapping):

    @lazy
    def default(self):
        try:
            return self[settings.DEFAULT_APPLICATION or iter(self).next()]
        except (KeyError, StopIteration):
            return None

    def __init__(self, owner):
        self._owner = owner
        self._lock = owner._lock
        self._items = {}
        self._queue = set()
        self._event = Event()
        self._known = set()

    owner = roproperty("_owner")
    lock = roproperty("_lock")

    def on_complete(self, item, restore):
        with self._lock:
            if item._id not in self._known:
                self._event.set()
            self._items[item._id] = item
            for subitem in item._objects.catalog.itervalues():
                managers.dispatcher.dispatch_handler(subitem, "on_startup")

    def new_sketch(self, restore=False):
        return (MemoryApplicationRestorationSketch if restore
            else MemoryApplicationSketch)(self)

    def new(self, name=DEFAULT_APPLICATION_NAME):
        item = self.new_sketch()
        item.id = str(uuid4())
        item.name = name
        return ~item

    def _exists(self, uuid):
        if self._queue:
            try:
                self._queue.remove(uuid)
            except KeyError:
                return False
            else:
                return True
        else:
            if managers.file_manager.exists(file_access.APPLICATION, uuid, settings.APPLICATION_FILENAME):
                return True
            else:
                self._explore()
                return False

    def _explore(self):
        self._queue = {filename for filename
            in managers.file_manager.list(file_access.APPLICATION)
            if complies(filename, verificators.uuid)} - set(self._items.keys())
        if not self._queue:
            self._queue = None

    def search(self, uuid_or_name):
        try:
            return self[uuid_or_name]
        except KeyError:
            with self._lock:
                for item in self.itervalues():
                    if item.name.lower().startswith(uuid_or_name):
                        return item
                raise

    def unload(self, uuid, remove=False):
        with self._lock:
            self._event.set()
            application = self._items[uuid]
            application.unimport_libraries()
            del self._items[uuid]

    def __getitem__(self, uuid):
        try:
            return self._items[uuid]
        except KeyError:
            if self._queue is None:
                raise
            else:
                with self._lock:
                    try:
                        return self._items[uuid]
                    except:
                        if self._queue is not None and self._exists(uuid):
                            self._known.add(uuid)
                            self._items[uuid] = item = self._owner.load_application(uuid, silently=True)
                            item.onstart()
                            return item
                        else:
                            raise

    def __iter__(self):
        with self._lock:
            self._event.clear()
            if self._queue is not None:
                self._explore()

            items = self._items.keys()
            if self._queue:
                items += self._queue

        for item in items:
            if self._event.is_set():
                raise RuntimeError("dictionary changed size during iteration")
            yield item

    def __len__(self):
        with self._lock:
            if self._queue is not None:
                self._explore()
            return len(self._items) + len(self._queue) if self._queue else len(self._items)

    def __str__(self):
        return "applications"
