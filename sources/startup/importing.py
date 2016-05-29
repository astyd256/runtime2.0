
import sys
import imp
import os
import os.path


def setup_settings(namespace):
    platform = sys.platform
    main_name = os.path.splitext(os.path.basename(sys.argv[0]))[0].lower()
    environment = os.environ.get("ENVIRONMENT", "development").lower()

    namespace["WINDOWS"] = platform.startswith("win")
    namespace["LINUX"] = platform.startswith("linux")
    namespace["FREEBSD"] = platform.startswith("frebsd")
    namespace["SERVER"] = main_name == "server"
    namespace["MANAGE"] = main_name == "manage"
    namespace["PRODUCTION"] = environment == "production"
    namespace["DEVELOPMENT"] = environment != "production"


class VDOM_settings_loader(object):

    _code = None
    _source = None

    def __init__(self, fullname, file, filename, suffixes):
        self._file = file
        self._filename = filename
        self._fullname = fullname
        self._suffix, self._mode, self._type = suffixes

    def load_module(self, fullname):
        if fullname != self._fullname:
            raise ImportError("Loader for module %s cannot handle module %s" % (self.fullname, fullname))

        code = self.get_code(fullname)
        module = sys.modules.setdefault(fullname, imp.new_module(fullname))

        module.__file__ = "<%s>" % self.__class__.__name__
        module.__loader__ = self
        if self._type == imp.PKG_DIRECTORY:
            module.__path__ = []
            module.__package__ = fullname
        else:
            module.__package__ = fullname.rpartition('.')[0]

        setup_settings(module.__dict__)

        exec(code, module.__dict__)
        return module

    def get_code(self, fullname=None):
        if fullname != self._fullname:
            raise ImportError("Loader for module %s cannot handle module %s" % (self.fullname, fullname))

        if self._code is None:
            if self._type == imp.PY_SOURCE:
                source = self.get_source(fullname)
                self._code = compile(source, self._filename, "exec")
            else:
                raise ImportError("Settings must be python source file")

        return self._code

    def get_source(self, fullname=None):
        if fullname != self._fullname:
            raise ImportError("Loader for module %s cannot handle module %s" % (self.fullname, fullname))

        if self._source is None:
            if self._type == imp.PY_SOURCE:
                if self._file.closed:
                    self._file = open(self._filename, 'rU')
                try:
                    self._source = self._file.read()
                finally:
                    self._file.close()
            else:
                raise ImportError("Settings must be python source file")

        return self._source

    def __repr__(self):
        return "<settings loader at 0x%08X>" % id(self)


class VDOM_settings_importer(object):

    def find_module(self, fullname, path=None):
        if fullname == "settings" and path is None:
            try:
                file, pathname, suffixes = imp.find_module(fullname)
            except ImportError:
                return None
            return VDOM_settings_loader(fullname, file, pathname, suffixes)
        else:
            return None

    def __repr__(self):
        return "<settings importer at 0x%08X>" % id(self)
