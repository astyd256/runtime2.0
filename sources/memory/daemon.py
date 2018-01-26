
from utils.threads import SmartDaemon
from logs import log
from file_access import FileWriter
import settings
import managers


class MemoryWriter(SmartDaemon):

    name = "Memory Writer"

    def __init__(self, manager):
        managers.file_manager.start_daemon()
        super(MemoryWriter, self).__init__(name=MemoryWriter.name,
            quantum=settings.QUANTUM, dependencies=FileWriter.name)
        self._manager = manager

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        self._manager.work()
        log.write("Stop %s\n" % self.name)

    def work(self):
        return self._manager.work()

    def __repr__(self):
        return "<memory writer at 0x%08X>" % id(self)


class MemoryCleaner(SmartDaemon):

    name = "Memory Cleaner"

    def __init__(self, manager):
        managers.file_manager.start_daemon()
        super(MemoryCleaner, self).__init__(name=MemoryCleaner.name,
            quantum=settings.QUANTUM, dependencies=FileWriter.name)
        self._manager = manager

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        self._manager.clean(everything=True)
        log.write("Stop %s\n" % self.name)

    def work(self):
        return self._manager.clean()

    def __repr__(self):
        return "<memory writer at 0x%08X>" % id(self)
