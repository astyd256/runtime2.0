
import datetime
import settings
from ..packer import create_packer
from ..formatters import TabbingLogFormatter
from ..baselog import BaseLog


NAME = "network"


class NetworkLogFormatter(TabbingLogFormatter):

    def __init__(self):
        super(NetworkLogFormatter, self).__init__(NAME)

    def format(self, timestamp, module, action, source, destination, user, resource):
        return super(NetworkLogFormatter, self).format(
            timestamp.strftime(settings.LOGGING_TIMESTAMP), module, action, source, destination, user, resource)

    def parse(self, entry):
        timestamp, module, action, source, destination, user, resource = super(NetworkLogFormatter, self).parse(entry)
        return datetime.datetime.strptime(timestamp, settings.LOGGING_TIMESTAMP), module, action, source, destination, user, resource


class NetworkLog(BaseLog):

    name = NAME
    formatter = NetworkLogFormatter
    packer = create_packer("SSSSSS")

    def accomplish(self, module, action, source, destination, user, resource):
        return datetime.datetime.utcnow(), module, action, source, destination, user, resource
