
from builtins import object
import sys
import imp
import os
import os.path
import io

from utils.console import CONSOLE_WIDTH


class SettingsImporter(object):

    def find_module(self, fullname, path=None):
        return self if fullname == "appsettings" and path is None else None

    def load_module(self, fullname):
        if fullname != "appsettings":
            raise ImportError("Settings loader cannot handle module \"%s\"" % fullname)
        fullname = "settings"
        module = sys.modules.get(fullname)
        if not module:
            module = imp.new_module(fullname)

        filename = fullname + ".pyc"
        if os.path.isfile(filename):
            with io.open(filename, "rb") as file:
                code = file.read()
        else:
            filename = fullname + ".py"
            if os.path.isfile(filename):
                with io.open(filename, "rU", encoding="utf8") as file:
                    source = file.read()
                code = compile(source, filename, "exec")
            else:
                raise ImportError("Unable to load \"%s\"" % fullname)

        module.__file__ = filename
        module.__loader__ = self
        module.__package__ = None

        platform = sys.platform
        filename = os.path.splitext(os.path.basename(sys.argv[0]))[0].lower()
        environment = os.environ.get("ENVIRONMENT", "development").lower()
        instance = os.environ.get("VDOM_INSTANCE_ID", "unknown")

        module.__dict__.update(
            WINDOWS=platform.startswith("win"),
            LINUX=platform.startswith("linux"),
            FREEBSD=platform.startswith("frebsd"),
            SERVER=filename == "server",
            MANAGE=filename == "manage",
            PRODUCTION=environment == "production",
            DEVELOPMENT=environment != "production",
            ENVIRONMENT=environment,
            INSTANCE=instance)

        sys.modules[fullname] = module
        exec(code, module.__dict__)

        if CONSOLE_WIDTH < module.__dict__.get("MANAGE_LINE_WIDTH"):
            module.__dict__["MANAGE_LINE_WIDTH"] = CONSOLE_WIDTH
            module.__dict__["MANAGE_NAME_WIDTH"] = CONSOLE_WIDTH * 30 // 100
            module.__dict__["MANAGE_LONG_NAME_WIDTH"] = CONSOLE_WIDTH * 70 // 100

        return module
    
    def find_spec(self, fullname, path, target=None):
        return self.find_module(fullname, path)