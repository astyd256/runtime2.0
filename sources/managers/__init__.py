
import sys
from threading import RLock


# def register(name, manager_class):
#     globals()[name] = manager_class()


# def has(*names):
#     namespace = globals()
#     for name in names:
#         if name not in namespace:
#             return False
#     return True

class Managers(object):

    __name__ = __name__

    def __init__(self):
        self._lock = RLock()
        self._lazy = {}

    def register(self, name, manager_class, lazy=False):
        with self._lock:
            if lazy:
                self._lazy[name] = manager_class
            else:
                setattr(self, name, manager_class())

    def has(self, *names):
        for name in names:
            if not (name in self.__dict__ or name in self._lazy):
                return False
        return True

    def __getattr__(self, name):
        with self._lock:
            instance = self.__dict__.get(name)
            if instance:
                return instance
            else:
                manager_class = self._lazy.get(name)
                if manager_class:
                    instance = manager_class()
                    setattr(self, name, instance)
                    return instance
                else:
                    raise AttributeError(name)


sys.modules[__name__] = Managers()
