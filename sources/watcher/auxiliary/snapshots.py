
import sys
import gc
import types
from threading import Lock

import settings
from logs import log
from utils.threads import SmartDaemon
from utils.tracing import CellType


EXCLUDE_TYPES = (types.FrameType, CellType, types.CodeType,
    types.FunctionType, types.LambdaType, types.GeneratorType,
    types.BuiltinMethodType, types.BuiltinFunctionType)


class WatcherSnapshooter(SmartDaemon):

    name = "Watcher Snapshooter"

    def _get_recent(self):
        with self._lock:
            if self._cache is None:
                self._cache = self._recent.copy()
            return self._cache

    recent = property(_get_recent)

    def _collect(self):
        check_interval = sys.getcheckinterval()
        sys.setcheckinterval(sys.maxint)
        try:
            return {id(object) for object in gc.get_objects() if not isinstance(object, EXCLUDE_TYPES)}
        finally:
            sys.setcheckinterval(check_interval)

    def prepare(self):
        log.write("Start " + self.name)

        self._lock = Lock()
        self._cache = None

        self._initial = self._collect()
        self._previous = set()
        self._recent = set()

        self._initial.update({id(self), id(self.__dict__), id(self._initial), id(self._recent)})

    def cleanup(self):
        log.write("Stop " + self.name)

    def work(self):
        log.write("Accumulate new objects")
        gc.collect()
        with self._lock:
            current = self._collect()
            current.difference_update(self._initial)
            current.discard(id(current))

            self._recent.intersection_update(current)
            self._recent.update(self._previous & current)

            self._previous = current
            self._cache = None

            log.write("Accumulate %d object(s)" % len(self._recent))
        return settings.WATCHER_SNAPSHOT_INTERVAL


class WatcherSnapshot(object):

    def __init__(self):
        self._lock = Lock()
        self._thread = None

    def _get_recent(self):
        with self._lock:
            if self._thread is None:
                return None
            else:
                recent = self._thread.recent
                return tuple(item for item in gc.get_objects() if id(item) in recent)

    recent = property(_get_recent)

    def start(self):
        with self._lock:
            if self._thread is not None:
                self._thread.stop()
                self._thread.join()
            self._thread = WatcherSnapshooter()
            self._thread.start()

    def stop(self):
        with self._lock:
            if self._thread is not None:
                self._thread.stop()
