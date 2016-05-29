
import datetime
from threading import current_thread
import settings
from ..packer import create_packer
from ..formatters import PrefixingLogFormatter
from ..debuglog import DebugLog


NAME = "server"
WIDTHS = 21, 22


class ServerLogFormatter(PrefixingLogFormatter):

    def __init__(self):
        super(ServerLogFormatter, self).__init__(NAME, WIDTHS)

    def format(self, timestamp, thread, module, level, message):
        return super(ServerLogFormatter, self).format(module, level, timestamp.strftime(settings.LOGGING_TIMESTAMP), thread, message)

    def parse(self, entry):
        module, level, timestamp, thread, message = super(ServerLogFormatter, self).parse(entry)
        return datetime.datetime.strptime(timestamp, settings.LOGGING_TIMESTAMP), thread, module, level, message


class ServerLog(DebugLog):

    name = NAME
    formatter = ServerLogFormatter
    packer = create_packer("TSSBS")

    def accomplish(self, module, level, message):
        return datetime.datetime.utcnow(), current_thread().name, module or "", level, message
