
import sys


def discover_calling_module():
    frame = sys._getframe(2)
    while 1:
        namespace = frame.f_globals
        logging = namespace.get("LOGGING", KeyError)
        if logging is None:
            frame = frame.f_back
            if frame is None:
                return None
        elif logging is KeyError:
            package = namespace.get("__package__")
            if package:
                return " ".join(part.capitalize() for part in package.split(".", 1)[0].split("_"))
            else:
                return None
        else:
            return logging
