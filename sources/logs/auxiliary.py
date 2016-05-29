
import sys


def get_calling_module():
    frame = sys._getframe(2)
    while True:
        namespace = frame.f_globals
        if namespace.get("LOGGING", KeyError) is None:
            frame = frame.f_back
            if frame is None:
                return
        else:
            package = namespace.get("__package__")
            if not package:
                return
            name = getattr(sys.modules[package], "LOGGING", None)
            if name:
                return name
            else:
                return " ".join(part.capitalize() for part in package.split(".", 1)[0].split("_"))
