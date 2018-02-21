
from utils.threads import SmartDaemon
from logs import log
from file_access import FileWriter
import settings
import managers


class CompilerCleaner(SmartDaemon):

    name = "Compiler Cleaner"

    def __init__(self, compiler):
        managers.file_manager.start_daemon()
        super(CompilerCleaner, self).__init__(name=CompilerCleaner.name,
            quantum=settings.QUANTUM, dependencies=FileWriter.name)
        self._compiler = compiler

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        log.write("Stop %s\n" % self.name)

    def work(self):
        return self._compiler.clean()

    def __repr__(self):
        return "<compiler cleaner at 0x%08X>" % id(self)
