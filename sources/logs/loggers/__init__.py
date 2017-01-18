
from importlib import import_module
import settings


Logger = import_module("logs.loggers.%s" % settings.LOGGER).Logger if settings.LOGGER else None
