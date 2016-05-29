
import sys
import os
from time import time
from logs import log
from utils.tracing import format_exception_trace, format_threads_trace
from .auxiliary import shutdown


INTERRUPT_EXIT_TIME = 0.4


def exithook():
    shutdown()


def excepthook(extype, exvalue, extraceback):
    if isinstance(exvalue, KeyboardInterrupt):
        log.write("Interrupt from keyboard\n")
        timestamp = time()
        while True:
            try:
                shutdown()
                break
            except KeyboardInterrupt:
                delta = time() - timestamp
                if delta < INTERRUPT_EXIT_TIME:
                    log.debug("Force exit due consecutive interrupts from keyboard\n")
                    os._exit(1)
                else:
                    log.debug("Show threads trace due interrupt from keyboard:\n%s" % format_threads_trace(indent="    "))
                    timestamp += delta
            except:
                sys.excepthook(*sys.exc_info())
    else:
        log.error(format_exception_trace(
            information=(extype, exvalue, extraceback),
            locals=True, threads=True, separate=True), module=False)
