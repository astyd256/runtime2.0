
import sys
import signal
from threading import current_thread, enumerate as enumerate_threads
from utils.tracing import format_thread_trace
import settings
import utils.threads
from .thread import SmartThread
from .daemon import SmartDaemon


SERVER_VARIABLE_NAME = "server"

SHUTDOWN_TIME_TO_NOTIFY = 3
SHUTDOWN_CONSECUTIVE_NOTIFICATIONS = True


def search(name):
    for thread in enumerate_threads():
        if not isinstance(thread, SmartThread):
            continue
        if thread.name == name:
            return thread


def wait(seconds=None):
    thread = current_thread()
    event = thread._event if isinstance(thread, SmartThread) else utils.threads.event
    remainder = settings.QUANTUM if seconds is None else seconds
    while remainder > 0:
        timeout = min(settings.QUANTUM, remainder)
        if event.wait(timeout):
            break
        remainder -= timeout
    event.clear()


def intercept(handler=None, ctrlc=None):
    if handler:
        def sigterm_handler(signum=None, frame=None):
            handler()
        signal.signal(signal.SIGTERM, sigterm_handler)
    if ctrlc:
        def sigint_handler(signum=None, frame=None):
            sys.stdout.write("Interrupt from keyboard")
            ctrlc()
        signal.signal(signal.SIGINT, sigint_handler)


def shutdown(quantum=settings.QUANTUM):
    server = getattr(utils.threads.main, SERVER_VARIABLE_NAME, None)
    if server:
        server.stop()

    def stop(condition):
        last, tries = None, 0
        while True:
            threads = tuple(thread for thread in enumerate_threads()
                if isinstance(thread, SmartThread) and condition(thread))
            if not threads:
                break
            for thread in threads:
                if not thread.stopping:
                    thread.stop()
            thread = threads[0]
            if thread == last:
                if tries == SHUTDOWN_TIME_TO_NOTIFY // quantum:
                    sys.stdout.write("Waiting for %s:\n%s" %
                        (thread.name, format_thread_trace(thread, indent="    ")))
                    if SHUTDOWN_CONSECUTIVE_NOTIFICATIONS:
                        tries = 0
            else:
                last, tries = thread, 0
            thread.join(quantum)
            tries += 1

    stop(lambda thread: not thread.latter and not isinstance(thread, SmartDaemon))
    stop(lambda thread: not thread.latter and isinstance(thread, SmartDaemon) and not thread.dependencies)
    stop(lambda thread: not isinstance(thread, SmartDaemon))
    stop(lambda thread: isinstance(thread, SmartDaemon) and not thread.dependencies)
    stop(lambda thread: True)
