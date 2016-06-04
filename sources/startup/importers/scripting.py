
import sys
import imp
import os
import os.path
import io
import re
import managers


MODULE_NAME_PATTERN = r"(?:module_)([A-F\d]{8}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{4}_[A-F\d]{12})"
LIBRARY_NAME_PATTERN = r"([A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12})(?:\.(.+))?"
FULLNAME_REGEX = re.compile(r"^%s|%s$" % (MODULE_NAME_PATTERN, LIBRARY_NAME_PATTERN), re.IGNORECASE)
SCRIPTING_MODULES = ("server", "application", "log", "session", "request", "response", "VDOM_object", "obsolete_request")


settings = None
file_access = None


class ScriptingFinder(object):

    def find_module(self, fullname, path=None):
        global settings, file_access, ScriptingFinder
        if getattr(managers, "file_manager", None) and getattr(managers, "engine", None):
            settings = __import__("settings")
            file_access = __import__("file_access")
            self.__class__ = ScriptingFinder = ActualScriptingFinder
            return self.find_module(fullname, path)
        else:
            return None


class ActualScriptingFinder(object):

    def find_module(self, fullname, path=None):

        def select_loader(fullname, location, loader_class, package=None):
            if location.endswith(".py"):
                location = location[:-3]
            filename = location + ".pyc"
            if os.path.isfile(filename):
                return loader_class(fullname, package=package, filename=filename)
            else:
                filename = location + ".py"
                if os.path.isfile(filename):
                    return loader_class(fullname, package=package, filename=filename)
                else:
                    return None

        match = FULLNAME_REGEX.match(fullname)
        if match:
            module = match.group(1)
            if module:
                location = managers.file_manager.locate(file_access.MODULE, module.replace("_", "-"))
                return select_loader(fullname, location, ScriptingLoader)
            else:
                package = match.group(2)
                library = match.group(3)
                if library:
                    application = managers.engine.application
                    if application is None:
                        return None
                    if package != application.id:
                        raise ImportError("Unable to load \"%s\" library from \"%s\" context" %
                            (package, application.id))
                    location = managers.file_manager.locate(file_access.LIBRARY, package, library)
                    return select_loader(fullname, location, ScriptingLoader, package=package)
                else:
                    location = managers.file_manager.locate(file_access.LIBRARY, package)
                    return ScriptingLoader(fullname, package=fullname, path=[location])

        return None


class ScriptingLoader(object):

    def __init__(self, fullname, package=None, path=None, filename=None):
        self._fullname = fullname
        self._package = package
        self._path = path
        self._filename = filename

    def load_module(self, fullname):
        if fullname != self._fullname:
            raise ImportError("Loader for module \"%s\" cannot handle module \"%s\"" % (self._fullname, fullname))

        module = sys.modules.get(self._fullname)
        if not module:
            module = imp.new_module(self._fullname)

        if self._filename:
            if self._filename.endswith(".py"):
                with io.open(self._filename, "rU", encoding="utf8") as file:
                    source = file.read()
                code = compile(source, self._filename, "exec")
            else:
                with io.open(self._filename, "rb") as file:
                    code = file.read()
        else:
            code = None

        module.__file__ = self._filename
        module.__loader__ = self
        module.__package__ = self._package
        if self._path:
            module.__path__ = self._path

        scripting = __import__("scripting")
        module.__dict__.update({name: getattr(scripting, name) for name in SCRIPTING_MODULES})

        sys.modules[self._fullname] = module
        if code:
            exec(code, module.__dict__)

        return module
