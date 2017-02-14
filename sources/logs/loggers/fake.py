
from utils.tracing import format_threads_trace
from utils.threads import SmartDaemon
from .. import log
from ..logger import BaseLogger


class Logger(BaseLogger):

    name = "Fake Logger"

    def ascribe(self, sublog):

        def enqueue(*arguments):
            pass

        return enqueue
