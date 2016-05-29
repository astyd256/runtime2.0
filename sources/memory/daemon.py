
from utils.threads import SmartDaemon
from logs import log
from file_access import FileWriter
import managers


QUANTUM = 0.5  # 30.1


class MemoryWriter(SmartDaemon):

    name = "Memory Writer"

    def __init__(self, manager):
        managers.file_manager.start_daemon()
        super(MemoryWriter, self).__init__(name=MemoryWriter.name,
            quantum=QUANTUM, dependencies=FileWriter.name)
        self._manager = manager

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        log.write("Stop %s\n" % self.name)
        self._manager.work()

    def work(self):
        return self._manager.work()

    def __repr__(self):
        return "<memory writer at 0x%08X>" % id(self)


VDOM_memory_writer = MemoryWriter
