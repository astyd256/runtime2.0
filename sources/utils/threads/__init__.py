
import sys
import atexit

from threading import current_thread, Event

import settings

from .thread import SmartThread, VDOM_thread
from .daemon import SmartDaemon, VDOM_daemon
from .server import SmartServer, VDOM_server
from .auxiliary import search, wait, intercept, shutdown
from .locals import localcontext, getlocal, setlocal, dellocal
from .hooks import excepthook, exithook


main = current_thread()
event = Event()


if main.name != "MainThread":
    raise Exception("Threads module must be initialized from main thread")
main.name = settings.MAIN_NAME

sys.excepthook = excepthook
atexit.register(exithook)
intercept(exithook)
