
import datetime
import settings
from ..packer import create_packer
from ..formatters import TabbingLogFormatter
from ..baselog import BaseLog


NAME = "security"


class SecurityLogFormatter(TabbingLogFormatter):

    def __init__(self):
        super(SecurityLogFormatter, self).__init__(NAME)

    def format(self, timestamp, module, user, action):
        return super(SecurityLogFormatter, self).format(
            timestamp.strftime(settings.LOGGING_TIMESTAMP), module, user, action)

    def parse(self, entry):
        timestamp, module, user, action = super(SecurityLogFormatter, self).parse(entry)
        return datetime.datetime.strptime(timestamp, settings.LOGGING_TIMESTAMP), module, user, action


class SecurityLog(BaseLog):

    name = NAME
    formatter = SecurityLogFormatter
    packer = create_packer("SSS")

    def accomplish(self, module, user, action):
        return datetime.datetime.utcnow(), module, user, action
