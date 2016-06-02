
from __future__ import absolute_import

import imp
import os
import os.path
import settings
import managers
from .generic import BaseLoader, BaseFinder


SCRIPTING_MODULES = ("server", "application", "log", "session", "request", "response", "VDOM_object", "obsolete_request")


class LibraryLoader(BaseLoader):

    def setup_module(self, module):
        namespace = module.__dict__
        scripting = __import__("scripting")
        for name in SCRIPTING_MODULES:
            namespace[name] = getattr(scripting, name)

    def __str__(self):
        return "library loader"


class LibraryFinder(BaseFinder):

    def find_module(self, fullname, path=None):
        engine = getattr(managers, "engine", None)
        if not engine:
            return

        application = engine.application
        if application is None:
            return None

        search_path = [os.path.join(settings.LIBRARIES_LOCATION, application.id)]
        try:
            file, pathname, description = imp.find_module(fullname, search_path)
        except ImportError:
            return None
        return LibraryLoader(fullname, file, pathname, description)

    def __str__(self):
        return "library finder"
