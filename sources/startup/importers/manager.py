
from builtins import object
import sys
import imp

from collections import defaultdict
# from threading import local

import managers

from logs import log


class ImportManagerLocal(object):  # local

    modules = defaultdict(dict)


class ImportManager(object):

    def __init__(self):
        self._local = ImportManagerLocal()

    def register(self, context, name, initializer):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to register library outside of application")
        context = ":".join((application.id, context))
        imp.acquire_lock()
        try:
            self._local.modules[context][name] = initializer
            if context not in sys.modules:
                __import__(context)
            del sys.modules[".".join((context, name))]
            del sys.modules[context].__dict__[name]
        except KeyError:
            pass
        finally:
            imp.release_lock()

    def unregister(self, context, name=None):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to unregister library outside of application")
        context = ":".join((application.id, context))
        if name is None:
            imp.acquire_lock()
            try:
                del self._local.modules[context]
                del sys.modules[context]
            except KeyError:
                pass
            finally:
                imp.release_lock()
        else:
            imp.acquire_lock()
            try:
                del self._local.modules[context][name]
                del sys.modules[".".join((context, name))]
                del sys.modules[context].__dict__[name]
            except KeyError:
                pass
            finally:
                imp.release_lock()

    def lookup(self, context, name=None):
        application = managers.engine.application
        if application is None:
            raise Exception("Unable to lookup library outside of application")
        context = ":".join((application.id, context))
        package = self._local.modules.get(context)
        if name is None:
            return package
        if package is None:
            return None
        else:
            return package.get(name)


class ImportManagerPackageLoader(object):

    def __init__(self, fullname):
        self._fullname = fullname

    def load_module(self, fullname):
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        module = imp.new_module(self._fullname)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []

        sys.modules[self._fullname] = module

        return module


class ImportManagerModuleLoader(object):

    def __init__(self, fullname, initializer):
        self._fullname = fullname
        self._initializer = initializer

    def load_module(self, fullname):
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        package = self._fullname.partition(".")[0]
        context, separator, name = package.partition(":")

        module = imp.new_module(self._fullname)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = package

        sys.modules[self._fullname] = module
        self._initializer(context, name, module.__dict__)

        return module
