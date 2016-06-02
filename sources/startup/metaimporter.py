
import sys
import imp
import pkgutil
import os.path

import settings
import managers


class VDOM_metaimporter(object):

    def __init__(self):
        sys.path.append(settings.LIBRARIES_LOCATION)

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
        return pkgutil.ImpLoader(fullname, file, pathname, description)

    def __repr__(self):
        return "<metaimporter at 0x%08X>" % id(self)
