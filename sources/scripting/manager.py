
import ctypes
from time import time
from threading import current_thread, RLock
from weakref import WeakKeyDictionary

from logs import log
from utils.tracing import describe_thread
from .executable import ExecutionTimeoutError
from .daemon import ScriptCleaner


class ScriptManager(object):

    def __init__(self):
        self._lock = RLock()
        self._threads = WeakKeyDictionary()
        self._cleaner = None

    def work(self):
        now = time()
        with self._lock:
            for thread, (counter, deadline) in list(self._threads.items()):
                if now > deadline:
                    log.warning("Terminate %s due to timeout" % describe_thread(thread))
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, ctypes.py_object(ExecutionTimeoutError))
                    self._threads.pop(thread, None)

    def start_cleaner(self):
        with self._lock:
            if self._cleaner is None:
                self._cleaner = ScriptCleaner(self)
                self._cleaner.start()
            return self._cleaner

    def ignore(self):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(current_thread().ident, None)

    def watch(self, timeout=60):
        thread = current_thread()
        with self._lock:
            values = self._threads.get(thread)
            if values is None:
                self._threads[thread] = 1, time() + timeout
            else:
                counter, deadline = self._threads[thread]
                self._threads[thread] = counter + 1, deadline
            if self._cleaner is None:
                self.start_cleaner()

    def cancel(self):
        thread = current_thread()
        with self._lock:
            try:
                counter, deadline = self._threads[thread]
            except KeyError:
                pass
            else:
                if counter == 1:
                    del self._threads[thread]
                else:
                    self._threads[thread] = counter - 1, deadline
