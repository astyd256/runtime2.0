
import sys


WINDOWS = sys.platform.startswith("win")
LINUX = sys.platform.startswith("linux")
FREEBSD = sys.platform.startswith("frebsd")


from .common import console_debug, set_virtual_card, login_virtual_card


if WINDOWS:
    from utils.system.windows import *
elif LINUX:
    from utils.system.linux import *
else:
    from utils.system.freebsd import *
