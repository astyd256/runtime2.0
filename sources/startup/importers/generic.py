
import sys
import imp


class BaseLoader(object):

    def __init__(self, fullname, file, filename, suffixes):
        self._fullname = fullname
        self._file = file
        self._filename = filename
        self._suffix, self._mode, self._type = suffixes
        self._source = None
        self._code = None

    def setup_module(self, module):
        pass

    def load_module(self, fullname):
        if fullname != self._fullname:
            raise ImportError("Loader for module \"%s\" cannot handle module \"%s\"" % (self.fullname, fullname))

        if fullname in sys.modules:
            raise ImportError("Module \"%s\" already loaded" % fullname)

        code = self._get_code()
        module = imp.new_module(fullname)

        module.__file__ = self._filename
        # module.__loader__ = self
        if self._type == imp.PKG_DIRECTORY:
            module.__path__ = []
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]

        self.setup_module(module)
        sys.modules[fullname] = module
        exec(code, module.__dict__)

        return module

    def _get_file(self):
        if not self._file:
            raise ImportError("No file to reopen")
        if self._file.closed:
            if self._type == imp.PY_SOURCE:
                self._file = open(self.filename, 'rU')
            elif self._type == imp.PY_COMPILED:
                self._file = open(self.filename, 'rb')
            else:
                raise ImportError("Unknown module type: %r" % self._type)
        return self._file

    def _get_source(self):
        if self._source is None:
            if self._type == imp.PY_SOURCE:
                with self._get_file() as file:
                    self._source = file.read()
            elif self._type == imp.PY_COMPILED:
                raise ImportError("Byte code is not supported")
            else:
                raise ImportError("Unknown module type: %r" % self._type)
        return self._source

    def _get_code(self):
        if self._code is None:
            if self._type == imp.PY_SOURCE:
                source = self._get_source()
                self._code = compile(source, self._fullname, "exec")
            elif self._type == imp.PY_COMPILED:
                raise ImportError("Byte code is not supported")
            else:
                raise ImportError("Unknown module type: %r" % self._type)
        return self._code

    def __str__(self):
        return "base loader"

    def __repr__(self):
        return "<%s at 0x%08X>" % (self, id(self))


class BaseFinder(object):

    def find_module(self, fullname, path=None):
        return None

    def __str__(self):
        return "base finder"

    def __repr__(self):
        return "<%s at 0x%08X>" % (self, id(self))
