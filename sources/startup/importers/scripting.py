
from builtins import object
import sys
import imp

from logs import log


class ScriptingPackageLoader(object):

    def __init__(self, fullname, modules):
        self._fullname = fullname
        self._modules = modules

    def load_module(self, fullname):
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        module = imp.new_module(self._fullname)
        module.__file__ = None
        module.__loader__ = self
        module.__package__ = self._fullname
        module.__path__ = []

        module.__dict__.update(self._modules)

        sys.modules[self._fullname] = module

        return module


class ScriptingModuleLoader(object):

    def __init__(self, fullname, executable):
        self._fullname = fullname
        self._executable = executable

    def load_module(self, fullname):
        if fullname != self._fullname:
            log.write("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))
            raise ImportError

        module = imp.new_module(self._fullname)
        module.__file__ = self._executable.signature
        module.__loader__ = self
        module.__package__ = self._executable.package

        sys.modules[self._fullname] = module
        self._executable.execute(None, module.__dict__)

        return module
