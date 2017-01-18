
from utils.tracing import format_threads_trace
from utils.threads import SmartDaemon
from . import log


class BaseLogger(SmartDaemon):

    name = "Base Logger"

    def __init__(self, condition=None, countdown=None):
        super(BaseLogger, self).__init__(name=type(self).name,
            condition=condition, countdown=countdown, latter=True)

    def ascribe(self, sublog):
        raise NotImplementedError

    def prepare(self):
        log.write("Start " + self.name)

    def cleanup(self):
        log.write("Remaining threads:\n%s" % format_threads_trace())
        log.write("Stop " + self.name)

    def work(self):
        pass
