
import sys
import imp
import os
import os.path
from .generic import BaseLoader, BaseFinder


class SettingsLoader(BaseLoader):

    def setup_module(self, module):
        namespace = module.__dict__

        platform = sys.platform
        filename = os.path.splitext(os.path.basename(sys.argv[0]))[0].lower()
        environment = os.environ.get("ENVIRONMENT", "development").lower()

        namespace["WINDOWS"] = platform.startswith("win")
        namespace["LINUX"] = platform.startswith("linux")
        namespace["FREEBSD"] = platform.startswith("frebsd")
        namespace["SERVER"] = filename == "server"
        namespace["MANAGE"] = filename == "manage"
        namespace["PRODUCTION"] = environment == "production"
        namespace["DEVELOPMENT"] = environment != "production"

    def __str__(self):
        return "settings loader"


class SettingsFinder(BaseFinder):

    def find_module(self, fullname, path=None):
        if fullname == "settings" and path is None:
            try:
                file, pathname, suffixes = imp.find_module(fullname)
            except ImportError:
                return None
            return SettingsLoader(fullname, file, pathname, suffixes)
        else:
            return None

    def __str__(self):
        return "settings finder"
