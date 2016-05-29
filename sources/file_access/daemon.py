
from utils.threads import SmartDaemon
from logs import log


class FileWriter(SmartDaemon):

    name = "File Writer"

    def __init__(self, manager):
        super(FileWriter, self).__init__(name=FileWriter.name)
        self._manager = manager

    def prepare(self):
        log.write("Start %s\n" % self.name)

    def cleanup(self):
        log.write("Stop %s\n" % self.name)
        self._manager.work()

    def work(self):
        return self._manager.work()

    def __repr__(self):
        return "<file manager writer at 0x%08X>" % id(self)


VDOM_file_manager_writer = FileWriter
