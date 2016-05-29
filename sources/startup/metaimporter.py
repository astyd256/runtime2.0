
import sys
import threading
import imp
import pkgutil

import settings


class VDOM_metaimporter(object):

    def __init__(self):
        sys.path.append(settings.LIBRARIES_LOCATION)

    def find_module(self, fullname, path=None):
        application = getattr(threading.currentThread(), "application", None)
        if application is None:
            return None

        if not fullname.startswith(application):
            return None

        if fullname == application:
            # load application
            search_path = [settings.LIBRARIES_LOCATION]
            try:
                file, pathname, description = imp.find_module(fullname, search_path)
            except ImportError:
                return None
            return pkgutil.ImpLoader(fullname, file, pathname, description)
        elif fullname.find(".") != -1:
            # load library
            (app_module, library) = fullname.split(".", 1)
            search_path = ["%s/%s" % (settings.LIBRARIES_LOCATION, app_module)]
            try:
                file, pathname, description = imp.find_module(library, search_path)
            except ImportError:
                return None
            return pkgutil.ImpLoader(fullname, file, pathname, description)
        else:
            return None

    def __repr__(self):
        return "<metaimporter at 0x%08X>" % id(self)
