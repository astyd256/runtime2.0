
import settings
from logs import log
from utils.threads import SmartDaemon


class ScriptCleaner(SmartDaemon):

    name = "Script Cleaner"

    def __init__(self, manager):
        super(ScriptCleaner, self).__init__(name=ScriptCleaner.name, quantum=settings.QUANTUM)
        self._manager = manager

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        log.write("Stop %s\n" % self.name)

    def work(self):
        return self._manager.work()

    def __repr__(self):
        return "<memory writer at 0x%08X>" % id(self)
