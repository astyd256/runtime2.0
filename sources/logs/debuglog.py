
import settings
import logs
from . import levels
from .auxiliary import get_calling_module
from .baselog import BaseLog


LOGGING = None


class DebugLog(BaseLog):

    def write(self, message=None, warning=None, error=None, debug=None, module=None, level=None, **options):
        if level is None:
            level, message = (levels.MESSAGE, message) if message is not None \
                else (levels.WARNING, warning) if warning is not None \
                else (levels.ERROR, error) if error is not None \
                else (levels.DEBUG, debug) if debug is not None \
                else (levels.MESSAGE, "")

        if level < settings.CONSOLE_LOG_LEVEL and level < settings.LOG_LEVEL:
            return

        if not isinstance(message, basestring):
            message = str(message)

        if module is None and settings.LOGGING_AUTOMODULE:
            module = get_calling_module()

        if settings.LOGGING:
            values = self.accomplish(module, level, message, **options)
            if level >= settings.LOG_LEVEL:
                self._enqueue(*values)
            if level >= settings.CONSOLE_LOG_LEVEL:
                logs.console.write(self._format(*values))
        elif level == levels.WARNING:
            if settings.DISPLAY_WARININGS_ANYWAY:
                logs.console.write(message, level=level)
        elif level == levels.ERROR:
            if settings.DISPLAY_ERRORS_ANYWAY:
                logs.console.write(message, level=level)

    def flush(self):
        if settings.LOGGING and self.echo:
            logs.console.flush()

    def debug(self, message, module=None, **options):
        self.write(message, module=module, level=levels.DEBUG, **options)

    def warning(self, message, module=None, **options):
        self.write(message, module=module, level=levels.WARNING, **options)

    def error(self, message, module=None, **options):
        self.write(message, module=module, level=levels.ERROR, **options)
