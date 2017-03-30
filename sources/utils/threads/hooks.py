
import sys
import os
from time import time
from threading import RLock
from logs import log
from utils.tracing import format_exception_trace, format_threads_trace
from utils.decorators import attributes
from .auxiliary import shutdown


INTERRUPT_EXIT_TIME = 0.4


@attributes(lock=RLock(), flag=False)
def initiate(cause=None):
    with initiate.lock:
        if initiate.flag:
            return
        else:
            initiate.flag = True

    log.write("Initiate shutdown%s...\n" % (" due to " + cause))
    timestamp = time()

    while True:
        try:
            shutdown()
            log.write("Shutdown complete\n")
            break
        except KeyboardInterrupt:
            delta = time() - timestamp
            if delta < INTERRUPT_EXIT_TIME:
                log.write("Force exit due to consecutive interrupts from keyboard\n")
                os._exit(1)
            else:
                log.write("Show threads trace due to interrupt from keyboard:\n%s" % format_threads_trace(indent="    "))
                timestamp += delta
        except:
            log.write("Force exit due to exception during shutdown")
            sys.excepthook(*sys.exc_info())
            os._exit(1)


def exithook():
    initiate()


def excepthook(extype, exvalue, extraceback):
    if isinstance(exvalue, KeyboardInterrupt):
        initiate(cause="interrupt from keyboard")
    else:
        log.error(format_exception_trace(
            information=(extype, exvalue, extraceback),
            locals=True, threads=True, separate=True), module=False)
