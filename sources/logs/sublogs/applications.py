
import datetime
from threading import current_thread
import settings
from ..packer import create_packer
from ..formatters import PrefixingLogFormatter
from ..debuglog import DebugLog


NAME = "applications"
WIDTHS = 21, 22, 22


class ApplicationsLogFormatter(PrefixingLogFormatter):

    def __init__(self):
        super(ApplicationsLogFormatter, self).__init__(NAME, WIDTHS)

    def format(self, timestamp, thread, module, level, user, message):
        return super(ApplicationsLogFormatter, self).format(module, level, timestamp.strftime(settings.LOGGING_TIMESTAMP), thread, user, message)

    def parse(self, entry):
        module, level, timestamp, thread, user, message = super(ApplicationsLogFormatter, self).parse(entry)
        return datetime.datetime.strptime(timestamp, settings.LOGGING_TIMESTAMP), thread, module, level, user, message


class ApplicationLog(DebugLog):

    name = NAME
    formatter = ApplicationsLogFormatter
    packer = create_packer("TSSBSS")

    def accomplish(self, module, level, message, user=None):
        return datetime.datetime.utcnow(), current_thread().name, module or "", level, user or "", message
